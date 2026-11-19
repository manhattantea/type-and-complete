# Part of 400_modules_import_system_and_sys_path (sibling module to main.py).

# In Odin or Go, every source file inside the same folder automatically shares
# one package namespace. Python takes the opposite design: every .py file is
# its own isolated module object backed by its own global dictionary (__dict__).
#
# Even though sibling_helper.py sits right beside main.py, neither file can see
# the other's names until one explicitly runs import sibling_helper (or
# from sibling_helper import ...). The first time any file imports this module,
# Python executes its top-level statements once and caches the resulting module
# object inside the global sys.modules dictionary. Importing sibling_helper
# from ten other files hands back that same cached object without re-running
# top-level code.
#
#     Suppose counter.py contains COUNT = 1 at module scope.
#     When main.py runs import counter, Python executes COUNT = 1 once and
#     stores the module in sys.modules["counter"]. A second import counter
#     anywhere in the process returns that exact same module object.

# Minimal anchor constant read by main.py on first run.
SIBLING_READY: bool = True

# Define a module-level constant MODULE_VERSION: str = "1.0.0" right below so
# main.py can read sibling_helper.MODULE_VERSION without modifying this file's
# anchor constant.


# Define def format_banner(title: str) -> str: returning a clean heading string
# such as f"[ {title} ]". Return the string instead of calling print() inside
# this helper so callers decide where and when to display it.


# Define def module_identity() -> tuple[str, str]: returning (__name__, __file__)
# so main.py can inspect what Python assigns to __name__ when a file is imported
# rather than run directly as __main__.
