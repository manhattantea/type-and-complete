# python 750_dynamic_code_exec_and_safe_literal_eval.py

import ast
import operator


def why_empty_builtins_eval_fails_and_literal_eval() -> None:

    # Calling eval(user_str) or exec(user_str) on untrusted input hands an
    # attacker arbitrary code execution. Even passing an empty builtins dict
    # like eval(user_str, {"__builtins__": {}}) does NOT make eval safe!
    #
    # Why does disabling __builtins__ fail as a sandbox? Because every Python
    # object carries inheritance links back to object. Starting from a bare
    # tuple literal (), an expression such as
    # ().__class__.__base__.__subclasses__() walks every loaded class in the
    # interpreter (including file and subprocess wrappers) without ever
    # touching __builtins__.
    #
    # When you only need to parse data literals from a string, ast.literal_eval
    # is the safe standard-library tool. It parses the string into an AST and
    # accepts ONLY literal data nodes: str, bytes, int, float, complex, tuple,
    # list, dict, set, bool, None, and unary + or - on numbers.
    #
    #     Suppose input_str is "__import__('os').system('echo pwned')":
    #     ast.literal_eval inspects the AST, sees an ast.Call node before any
    #     bytecode runs, and immediately raises ValueError.

    sample_tuple = ast.literal_eval("(10, 20)")
    print("Starter literal_eval result =", sample_tuple)

    # Parse config_raw = "{'host': '127.0.0.1', 'ports': (80, 443), 'active': True}"
    # using ast.literal_eval(config_raw) and print the resulting dictionary.


    # Verify ast.literal_eval rejects executable expressions before running them:
    # Inside try / except ValueError as err:, call
    # ast.literal_eval("__import__('os').system('echo pwned')") and print the
    # caught ValueError. Test a second payload such as "().__class__.__base__"
    # inside another try / except ValueError block.


def whitelisted_ast_calculator() -> None:

    # Sometimes literal_eval is too strict because you want simple arithmetic
    # formulas like "2 * (10 + 5) - 3" without allowing calls or lookups. The
    # clean pattern is a tiny whitelisted AST evaluator:
    # - Parse with ast.parse(expr_str, mode="eval").body.
    # - Recursively evaluate ONLY an explicit allow-list of node types:
    #   ast.Constant, ast.BinOp, and ast.UnaryOp mapped to functions from the
    #   operator module (operator.add, operator.sub, operator.mul,
    #   operator.truediv, operator.pos, operator.neg).
    # - Reject every other node type (ast.Call, ast.Attribute, ast.Name,
    #   ast.Pow) with ValueError.
    #
    #     Suppose you evaluate "2 * (3 + 4)":
    #     _eval_node sees BinOp(op=Mult), evaluates left=Constant(2) -> 2.0,
    #     then recurses into right=BinOp(op=Add) -> 3.0 + 4.0 = 7.0, and
    #     returns operator.mul(2.0, 7.0) = 14.0 without touching eval().
    #
    # Watch out for one classic Python gotcha when checking ast.Constant:
    # bool is a subclass of int, so isinstance(True, int) is True!
    #
    #     Suppose a user passes "True + 1":
    #     If you only check isinstance(node.value, (int, float)), True slips
    #     through as 1. Checking not isinstance(node.value, bool) blocks it.

    baseline = operator.add(2, 3)
    print("Starter operator.add(2, 3) =", baseline)

    # Write def safe_calc(expr_str: str) -> float: that parses
    # tree = ast.parse(expr_str, mode="eval") and evaluates tree.body via an
    # inner helper def _eval_node(node: ast.AST) -> float:
    # - Map ast.Add: operator.add, ast.Sub: operator.sub,
    #   ast.Mult: operator.mul, ast.Div: operator.truediv.
    # - Map ast.UAdd: operator.pos, ast.USub: operator.neg.
    # - If isinstance(node, ast.Constant): accept int or float ONLY when
    #   not isinstance(node.value, bool) and return float(node.value).
    # - If isinstance(node, ast.BinOp) and type(node.op) in bin_ops:
    #   evaluate left and right recursively and apply the mapped function.
    # - If isinstance(node, ast.UnaryOp) and type(node.op) in unary_ops:
    #   evaluate node.operand recursively and apply the mapped function.
    # - For anything else, raise ValueError(f"Unsupported expression: {ast.dump(node)}").


    # Test safe_calc inside this section:
    # - Print safe_calc("2 * (10 + 5) - 3") (expected: 27.0) and
    #   safe_calc("-4 + 10 / 2") (expected: 1.0).
    # - Inside try / except (ValueError, SyntaxError) as err:, confirm that
    #   "__import__('os').system('id')", "True + 1", and "2 ** 99999999" all
    #   raise ValueError cleanly.
    # - Test malformed syntax such as "2 + * 3" and division by zero "10 / 0"
    #   inside try / except (SyntaxError, ZeroDivisionError) as err: to verify
    #   both failure modes surface predictably without crashing the caller.


    # Extend your tests with a small batch loop over valid and invalid inputs:
    # pairs = [("10 - 3 * 2", 4.0), ("+5", 5.0), ("-(2 + 6)", -8.0)]
    # Verify each expression equals its expected float result.


def main() -> None:

    print("=== 1. Why empty __builtins__ fails and ast.literal_eval ===")
    why_empty_builtins_eval_fails_and_literal_eval()

    print("\n=== 2. Whitelisted AST arithmetic evaluator ===")
    whitelisted_ast_calculator()


if __name__ == "__main__":
    main()
