# python 740_ast_parsing_walking_and_transforming.py

import ast


def parsing_modes_and_ast_walk() -> None:

    # Python does not hide its compiler pipeline behind closed doors: the
    # standard-library ast module exposes the exact Abstract Syntax Tree
    # produced by CPython's parser. Linters like ruff, coverage plugins, and
    # test frameworks like pytest all inspect or rewrite these ast.AST nodes
    # before bytecode is ever emitted.
    #
    # When you call ast.parse(source, mode=...), the mode argument controls the
    # grammar rule at the root of the tree:
    # - mode="exec" parses zero or more statements and returns an
    #   ast.Module(body=[...]) node.
    # - mode="eval" parses one single expression and returns an
    #   ast.Expression(body=...) node, which is what compile(..., "<ast>", "eval")
    #   and eval(...) expect.
    #
    #     Suppose you parse "1 + 2" with mode="eval":
    #     ast.parse("1 + 2", mode="eval") returns
    #     Expression(body=BinOp(left=Constant(1), op=Add(), right=Constant(2))).
    #     If you passed "x = 1" with mode="eval", Python would raise SyntaxError
    #     because assignment is a statement, not an expression.
    #
    # To inspect every node quickly, ast.walk(tree) yields nodes in breadth-first
    # order without tracking parent links.

    sample_expr = ast.parse("1 + 2", mode="eval")
    print("Starter AST dump:", ast.dump(sample_expr))

    # Compare mode="exec" and mode="eval" directly:
    # Parse snippet = "x = 10\ny = x + 5" using ast.parse(snippet, mode="exec")
    # and print ast.dump(tree, indent=2) to see the Module body list.
    # Then inside try / except SyntaxError as err:, call
    # ast.parse("x = 10", mode="eval") and print the SyntaxError message.


    # Walk every node with ast.walk(tree):
    # Parse target_src = "total = (1 + 2) * 3\nprint(total)" with mode="exec".
    # Loop for node in ast.walk(target_src_tree):, collect type(node).__name__
    # into a list, and count how many ast.Constant nodes appear using
    # isinstance(node, ast.Constant). Print both results.


def node_visitor_and_generic_visit_trap() -> None:

    # While ast.walk(tree) is great for flat counts, ast.NodeVisitor gives you
    # targeted dispatch: when visitor.visit(tree) reaches an ast.Call node, it
    # automatically looks for a method named visit_Call(self, node). If no
    # specific method exists, it falls back to self.generic_visit(node), which
    # recurses into all child nodes.
    #
    # Here is the #1 trap with ast.NodeVisitor: the moment you define your own
    # visit_Call(self, node), NodeVisitor stops recursing into node's children
    # unless you explicitly call self.generic_visit(node) inside it!
    #
    #     Suppose your code contains outer(print("hi")):
    #     - Outer ast.Call is outer(...), with print("hi") inside its args list.
    #     - If visit_Call checks node.func.id == "print" and returns WITHOUT
    #       calling self.generic_visit(node), Python visits outer, sees it is
    #       not "print", and never enters args—silently missing print("hi")!
    #     - Calling self.generic_visit(node) at the end of visit_Call visits
    #       every argument and keyword value, catching the nested print call.

    demo_tree = ast.parse("len('abc')", mode="eval")
    call_count = sum(1 for n in ast.walk(demo_tree) if isinstance(n, ast.Call))
    print("Starter ast.Call count in len('abc'):", call_count)

    # Write class PrintCallFinder(ast.NodeVisitor): inside this function (or at
    # module scope) to collect the line numbers of every print(...) call:
    # - In def __init__(self) -> None:, initialize self.lines: list[int] = [].
    # - In def visit_Call(self, node: ast.Call) -> None:, check whether
    #   isinstance(node.func, ast.Name) and node.func.id == "print", and if so
    #   append node.lineno to self.lines.
    # - Always call self.generic_visit(node) so nested calls are still visited.


    # Test PrintCallFinder on a multi-line snippet containing at least three
    # print(...) calls, including one nested inside another call such as
    # len(str(print("inner"))) and one inside an if block.
    # Parse with ast.parse(snippet, mode="exec"), run finder = PrintCallFinder();
    # finder.visit(tree), and print finder.lines.


    # Write a second visitor class NameCollector(ast.NodeVisitor): that collects
    # every variable name read vs. assigned by checking isinstance(node.ctx, ast.Load)
    # and isinstance(node.ctx, ast.Store) inside visit_Name(self, node: ast.Name) -> None:.
    # Test it on "x = 1\ny = x + 2" and print both sets of names.


def node_transformer_and_fix_missing_locations() -> None:

    # ast.NodeTransformer works like NodeVisitor, except return values rewrite
    # the tree in place:
    # - Returning a new or modified ast.AST node replaces the original node.
    # - Returning None deletes a statement from a statement list such as
    #   Module.body or If.body.
    #
    # Traversal order matters when transforming expressions bottom-up. If you
    # call self.generic_visit(node) BEFORE inspecting node.left and node.right,
    # child BinOp nodes fold first:
    #
    #     Suppose the expression is (2 + 3) * 4:
    #     - visit_BinOp enters the outer Mult node and calls self.generic_visit(node).
    #     - The inner Add node (2 + 3) folds into ast.Constant(value=5).
    #     - Back in the outer Mult node, node.left is now Constant(5) and
    #       node.right is Constant(4), so it folds all the way to Constant(20)!
    #
    # Two sharp edges appear when creating fresh AST nodes:
    # - bool subclasses int in Python (isinstance(True, int) is True), so check
    #   type(val) is int rather than isinstance(val, int) when folding integers.
    # - Manually constructed nodes like ast.Constant(value=20) lack lineno and
    #   col_offset source coordinates. compile() rejects the tree unless you
    #   run ast.fix_missing_locations(tree) first.
    # - ast.unparse(tree) turns any AST back into clean Python source code,
    #   noting that comments and original whitespace are not stored in the AST.

    raw_tree = ast.parse("2 + 3", mode="eval")
    print("Starter unparsed expression:", ast.unparse(raw_tree))

    # Write class ConstantFolder(ast.NodeTransformer): overriding
    # def visit_BinOp(self, node: ast.BinOp) -> ast.AST:
    # - Call self.generic_visit(node) first for bottom-up folding.
    # - Verify isinstance(node.left, ast.Constant) and isinstance(node.right, ast.Constant)
    #   and type(node.left.value) is int and type(node.right.value) is int.
    # - If isinstance(node.op, ast.Add), return ast.Constant(value=node.left.value + node.right.value).
    # - If isinstance(node.op, ast.Mult), return ast.Constant(value=node.left.value * node.right.value).
    # - Otherwise return node.


    # Parse expr_tree = ast.parse("(2 + 3) * 4", mode="eval"), run
    # folded = ConstantFolder().visit(expr_tree), and call
    # ast.fix_missing_locations(folded).
    # Print ast.unparse(folded) (expected: "20"), then evaluate
    # eval(compile(folded, "<ast>", "eval")) and print the integer result.
    #
    # Try commenting out ast.fix_missing_locations(folded) before compile(...)
    # to see Python reject AST nodes that lack lineno and col_offset!


    # Practice deleting statements with NodeTransformer:
    # Write class StripPassStatements(ast.NodeTransformer): with
    # def visit_Pass(self, node: ast.Pass) -> ast.AST | None: returning None.
    # Parse "if True:\n    pass\n    x = 1", transform it, and print ast.unparse(cleaned).


def main() -> None:

    print("=== 1. Parsing modes and ast.walk ===")
    parsing_modes_and_ast_walk()

    print("\n=== 2. NodeVisitor and the generic_visit trap ===")
    node_visitor_and_generic_visit_trap()

    print("\n=== 3. NodeTransformer and fix_missing_locations ===")
    node_transformer_and_fix_missing_locations()


if __name__ == "__main__":
    main()
