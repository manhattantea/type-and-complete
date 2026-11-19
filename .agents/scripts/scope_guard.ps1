$ErrorActionPreference = 'Stop'

function Return-Decision([string]$Decision, [string]$Reason = '') {
    $obj = @{ decision = $Decision }
    if ($Reason) {
        $obj.reason = $Reason
    }
    $obj | ConvertTo-Json -Compress
    exit 0
}

function Normalize-Dir([string]$Path) {
    if ([string]::IsNullOrWhiteSpace($Path)) { return $null }
    try {
        $full = [System.IO.Path]::GetFullPath($Path.Trim()).TrimEnd('\', '/')
        return $full
    } catch {
        return $null
    }
}

function Is-WithinRoots([string]$FullPath, [string[]]$Roots) {
    if ([string]::IsNullOrWhiteSpace($FullPath)) { return $false }
    $norm = Normalize-Dir $FullPath
    if (-not $norm) { return $false }
    foreach ($root in $Roots) {
        if ($norm.Equals($root, [System.StringComparison]::OrdinalIgnoreCase)) {
            return $true
        }
        $prefix = $root + '\'
        if ($norm.StartsWith($prefix, [System.StringComparison]::OrdinalIgnoreCase)) {
            return $true
        }
    }
    return $false
}

function Test-SafePathToken([string]$Text, [string[]]$Roots) {
    if ([string]::IsNullOrEmpty($Text)) { return $true }

    # Block parent directory traversal segments (even wrapped in quotes or parens).
    if ($Text -match '(^|[\\/"''`(])\.\.([\\/"''`)]|$)') { return $false }

    # Block home directory shorthands and UNC/network paths.
    if ($Text -match '^~($|[\\/])') { return $false }
    if ($Text -match '^(\\\\|//)') { return $false }

    # Block root-relative paths like \Windows or /etc.
    if ($Text -match '^[\\/]') { return $false }

    # Block environment variables or hidden variable references inside strings.
    if ($Text -match '(?i)\$env:' -or $Text -match '(?i)\$home\b') { return $false }

    # Block PSDrive prefixes and URIs when not a switch like -File.
    if ($Text -notmatch '^-' -and $Text -match '(?i)^(HKLM|HKCU|HKCR|HKU|HKCC|Env|Alias|Function|Variable|Cert|WSMan|file|http|https):') { return $false }

    # If a Windows drive letter appears, ensure it is a rooted path strictly inside workspace roots.
    $trimmed = $Text.Trim('"', "'", '(', ')')
    if ($trimmed -match '^[A-Za-z]:') {
        if ($trimmed -notmatch '^[A-Za-z]:[\\/]') { return $false }
        if (-not (Is-WithinRoots $trimmed $Roots)) { return $false }
    }

    return $true
}

try {
    $raw = [Console]::In.ReadToEnd()
    if ([string]::IsNullOrWhiteSpace($raw)) {
        Return-Decision 'ask' 'Empty hook input.'
    }

    $payload = $raw | ConvertFrom-Json
    if (-not $payload -or -not $payload.toolCall -or $payload.toolCall.name -ne 'run_command') {
        Return-Decision 'ask' 'Not a run_command call.'
    }

    $roots = @()
    if ($payload.workspacePaths) {
        foreach ($wp in $payload.workspacePaths) {
            $n = Normalize-Dir $wp
            if ($n) { $roots += $n }
        }
    }
    if ($roots.Count -eq 0) {
        $repoFallback = Normalize-Dir (Split-Path -Parent (Split-Path -Parent $PSScriptRoot))
        if ($repoFallback) { $roots += $repoFallback }
    }
    if ($roots.Count -eq 0) {
        Return-Decision 'ask' 'No workspace root resolved.'
    }

    if ($payload.cwd) {
        if (-not (Is-WithinRoots $payload.cwd $roots)) {
            Return-Decision 'ask' 'Working directory is outside workspace root.'
        }
    }

    $argsObj = $payload.toolCall.args
    $cmdLine = $null
    if ($argsObj.PSObject.Properties['CommandLine']) {
        $cmdLine = [string]$argsObj.CommandLine
    } elseif ($argsObj.PSObject.Properties['command']) {
        $cmdLine = [string]$argsObj.command
    }

    if ([string]::IsNullOrWhiteSpace($cmdLine)) {
        Return-Decision 'ask' 'Empty CommandLine.'
    }

    $tokens = $null
    $errors = $null
    $ast = [System.Management.Automation.Language.Parser]::ParseInput($cmdLine, [ref]$tokens, [ref]$errors)
    if ($errors -and $errors.Count -gt 0) {
        Return-Decision 'ask' 'Unparseable shell command.'
    }

    # Reject writes via redirection, assignments, arbitrary .NET calls, type expressions, or string concat obfuscation.
    $disallowedNodes = $ast.FindAll({
        param($node)
        $node -is [System.Management.Automation.Language.RedirectionAst] -or
        $node -is [System.Management.Automation.Language.AssignmentStatementAst] -or
        $node -is [System.Management.Automation.Language.InvokeMemberExpressionAst] -or
        $node -is [System.Management.Automation.Language.TypeExpressionAst] -or
        $node -is [System.Management.Automation.Language.UsingExpressionAst] -or
        ($node -is [System.Management.Automation.Language.BinaryExpressionAst] -and
         $node.Operator -eq [System.Management.Automation.Language.TokenKind]::Plus)
    }, $true)

    if ($disallowedNodes.Count -gt 0) {
        Return-Decision 'ask' 'Contains redirection, assignment, concat, or method call.'
    }

    # Audit every string literal anywhere in the AST for path safety.
    $stringNodes = $ast.FindAll({
        param($node)
        $node -is [System.Management.Automation.Language.StringConstantExpressionAst] -or
        $node -is [System.Management.Automation.Language.ExpandableStringExpressionAst]
    }, $true)
    foreach ($sn in $stringNodes) {
        if (-not (Test-SafePathToken $sn.Value $roots)) {
            Return-Decision 'ask' 'String literal path outside project root requires review.'
        }
    }

    # Only allow safe pipeline variable $_ / $PSItem (blocks $env:*, $HOME, custom path vars).
    $vars = $ast.FindAll({
        param($node)
        $node -is [System.Management.Automation.Language.VariableExpressionAst]
    }, $true)
    foreach ($v in $vars) {
        $vName = $v.VariablePath.UserPath
        if ($vName -ne '_' -and $vName -ne 'PSItem') {
            Return-Decision 'ask' "Variable access `$$vName requires review."
        }
    }

    $allowedCmdlets = @(
        'Get-ChildItem', 'gci', 'dir', 'ls',
        'Get-Content', 'gc', 'cat', 'Get-Item', 'gi',
        'Select-String', 'sls', 'Test-Path', 'Resolve-Path',
        'Measure-Object', 'measure', 'Select-Object', 'select',
        'Sort-Object', 'sort', 'Where-Object', 'where',
        'ForEach-Object', 'foreach', 'Format-Table', 'ft', 'Write-Output'
    )

    $commands = $ast.FindAll({
        param($node)
        $node -is [System.Management.Automation.Language.CommandAst]
    }, $true)

    if ($commands.Count -eq 0) {
        Return-Decision 'ask' 'No command AST found.'
    }

    foreach ($c in $commands) {
        if ($c.InvocationOperator -ne [System.Management.Automation.Language.TokenKind]::Unknown) {
            Return-Decision 'ask' 'Invocation operators (& or .) require review.'
        }
        $name = $c.GetCommandName()
        if ([string]::IsNullOrWhiteSpace($name)) {
            Return-Decision 'ask' 'Dynamic command invocation requires review.'
        }

        $elemTexts = @()
        for ($i = 1; $i -lt $c.CommandElements.Count; $i++) {
            $el = $c.CommandElements[$i]
            if ($el -is [System.Management.Automation.Language.ScriptBlockExpressionAst]) {
                continue
            }
            if ($el -is [System.Management.Automation.Language.CommandParameterAst]) {
                $elemTexts += ('-' + $el.ParameterName)
                if ($el.Argument) {
                    $elemTexts += $el.Argument.Extent.Text.Trim('"', "'")
                }
                continue
            }
            $rawText = $el.Extent.Text
            if ($el -is [System.Management.Automation.Language.StringConstantExpressionAst]) {
                $rawText = $el.Value
            } elseif ($el -is [System.Management.Automation.Language.ExpandableStringExpressionAst]) {
                $rawText = $el.Value
            }
            $elemTexts += $rawText
        }

        $isOdin = $name.Equals('odin', [System.StringComparison]::OrdinalIgnoreCase) -or
                  $name.Equals('odin.exe', [System.StringComparison]::OrdinalIgnoreCase)
        $isRg = $name.Equals('rg', [System.StringComparison]::OrdinalIgnoreCase) -or
                $name.Equals('rg.exe', [System.StringComparison]::OrdinalIgnoreCase)

        if ($isOdin) {
            if ($elemTexts.Count -lt 1 -or ($elemTexts[0] -notin @('check', 'run', 'build', 'test', 'version', 'root', 'report'))) {
                Return-Decision 'ask' 'Unsupported odin subcommand requires review.'
            }
            foreach ($arg in $elemTexts) {
                if ($arg -match '^-extra-linker-flags(:|$)') {
                    Return-Decision 'ask' 'Linker flag overrides require review.'
                }
                if ($arg -match '^[A-Za-z0-9_-]+=(.+)$') {
                    if (-not (Test-SafePathToken $Matches[1] $roots)) {
                        Return-Decision 'ask' 'Path outside project root requires review.'
                    }
                }
                if (-not (Test-SafePathToken $arg $roots)) {
                    Return-Decision 'ask' 'Path outside project root requires review.'
                }
            }
            continue
        }

        if ($isRg) {
            foreach ($arg in $elemTexts) {
                if ($arg -in @('--pre', '-z', '--search-zip')) {
                    Return-Decision 'ask' 'External preprocessor flags require review.'
                }
                if (-not (Test-SafePathToken $arg $roots)) {
                    Return-Decision 'ask' 'Path outside project root requires review.'
                }
            }
            continue
        }

        $matchedCmdlet = $false
        foreach ($allowed in $allowedCmdlets) {
            if ($name.Equals($allowed, [System.StringComparison]::OrdinalIgnoreCase)) {
                $matchedCmdlet = $true
                break
            }
        }
        if (-not $matchedCmdlet) {
            Return-Decision 'ask' "Command '$name' is not in read-only allowlist."
        }

        foreach ($arg in $elemTexts) {
            if ($arg -match '^(?i)-Force$' -and $name -notin @('Get-ChildItem', 'gci', 'dir', 'ls')) {
                Return-Decision 'ask' 'Force flag requires review.'
            }
            if (-not (Test-SafePathToken $arg $roots)) {
                Return-Decision 'ask' 'Path outside project root requires review.'
            }
        }
    }

    Return-Decision 'auto_approve' 'Read-only workspace-scoped command verified.'
} catch {
    Return-Decision 'ask' 'Guard script exception fallback.'
}
