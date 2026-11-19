# python 120_varargs_kwargs_and_signature_markers.py

from typing import Any


def positional_only_and_keyword_only_markers() -> None:

    # In Python, every ordinary parameter name is implicitly part of your public
    # API because callers are allowed to pass it by keyword (fn(x=1)). That
    # creates two common maintenance traps:
    # - If you write def get(url, **headers) and a caller invokes
    #   get("https://api.local", url="custom-header"), Python raises TypeError
    #   because "url" collided with the positional parameter name.
    # - If a helper has several optional flags (timeout, retries, verify_tls),
    #   calls like fetch(url, 5.0, 3, True) are unreadable and break whenever
    #   you insert a new option.
    #
    # Python's / (positional-only marker) and * (keyword-only marker) fix both.
    # Every Python parameter list follows this exact left-to-right layout:
    #
    #     def f(pos_only, /, pos_or_kw, *args, kw_only, **kwargs):
    #
    # Everything before / MUST be passed positionally; its parameter name is
    # invisible to keyword matching, so it can never collide with **kwargs and
    # can be renamed safely later. Everything after * (or after *args) MUST be
    # passed by keyword.
    #
    #     Suppose def clamp(value: int, /, *, lo: int = 0, hi: int = 10) -> int:
    #     clamp(15, lo=0, hi=10) works and returns 10.
    #     clamp(value=15) raises TypeError because value sits before /.
    #     clamp(15, 0, 10) raises TypeError because lo and hi sit after *.

    def clamp(value: int, /, *, lo: int = 0, hi: int = 10) -> int:

        return min(max(value, lo), hi)

    print(f"Starter clamp(15, lo=0, hi=10) = {clamp(15, lo=0, hi=10)}")

    # Define send_request(method: str, url: str, /, *, timeout: float = 5.0, follow_redirects: bool = True, **headers: str) -> str
    # returning a summary string such as:
    # f"{method} {url} | timeout={timeout} | redirects={follow_redirects} | headers={headers}"
    # Call send_request("GET", "https://api.local", timeout=2.0, Authorization="Bearer xyz")
    # and print the result.


    # Prove why / prevents parameter-name collisions with **headers:
    # Call send_request("POST", "https://api.local", url="https://override.local", method="HEAD")
    # and print the returned string—notice "url" and "method" land cleanly inside
    # the headers dict instead of raising TypeError!


    # Error experiments for / and * enforcement:
    # After defining send_request above, try uncommenting each line one at a
    # time to see the exact TypeError messages Python produces:
    #
    # Positional-only argument passed by keyword:
    # print(send_request(method="GET", url="https://api.local"))
    #
    # Keyword-only argument passed positionally:
    # print(send_request("GET", "https://api.local", 2.0))


def variadic_args_and_kwargs_packing() -> None:

    # When a function accepts a variable number of arguments, *args and **kwargs
    # pack the extras automatically:
    # - *args: int gathers any remaining positional arguments into a tuple[int, ...].
    #   Notice the type annotation describes each individual item (int), NOT
    #   tuple[int, ...].
    # - Because *args already marks the keyword-only boundary, any named
    #   parameter placed after *args is automatically keyword-only (and you
    #   cannot place another bare * after *args).
    # - **kwargs: Any gathers any unmatched keyword arguments into a
    #   dict[str, Any]. Again, the annotation describes each dict value's type.
    #
    #     Suppose def log_tags(topic: str, *tags: str, upper: bool = False):
    #     Calling log_tags("net", "tcp", "tls", upper=True) binds topic="net",
    #     tags=("tcp", "tls"), and upper=True.

    def count_items(*items: str) -> tuple[int, tuple[str, ...]]:

        return len(items), items

    print(f"Starter *args packing: {count_items('alpha', 'beta')}")

    # Define summarize_scores(label: str, *scores: int, precision: int = 2) -> str
    # where label is positional-or-keyword, scores captures zero or more ints,
    # and precision is keyword-only because it follows *scores.
    # When scores is empty, return f"{label}: no scores"; otherwise return
    # f"{label}: avg={sum(scores) / len(scores):.{precision}f}".
    # Call summarize_scores("quiz", 88, 92, 95, precision=1) and
    # summarize_scores("empty") and print both.


    # Define inspect_kwargs(**kwargs: Any) -> dict[str, Any] returning kwargs.
    # Call inspect_kwargs(debug=True, workers=4, mode="fast"), print the dict,
    # and verify type(result) is dict.


    # Write a forwarding adapter helper—a pattern used throughout decorators
    # and wrappers:
    # Define forward_call(fn: Any, *args: Any, **kwargs: Any) -> Any that prints
    # args and kwargs and returns fn(*args, **kwargs).
    # Test it by calling forward_call(summarize_scores, "lab", 80, 90, precision=1).


def call_site_unpacking_and_composition() -> None:

    # Putting * or ** at a CALL SITE does the inverse of packing in a def header:
    # - *iterable unpacks any iterable (tuple, list, range, generator) into
    #   separate positional arguments.
    # - **mapping unpacks any string-keyed dict into separate keyword arguments.
    # You can even unpack multiple iterables and multiple dicts in the same call,
    # as long as no keyword name is supplied twice (duplicate keys raise
    # TypeError: got multiple values for keyword argument).
    #
    #     Suppose bounds = (2, 10) and opts = {"sep": " -> "}.
    #     Calling print(*bounds, **opts) executes print(2, 10, sep=" -> ").

    pair = (2, 10)
    print(f"Starter call-site unpacking pow(*{pair}) = {pow(*pair)}")

    # Define a small local helper format_req(method: str, url: str, /, *, timeout: float = 5.0, **headers: str) -> str
    # returning f"{method} {url} ({timeout}s) {headers}".
    # Create endpoint = ("PUT", "https://api.local/v1/items") and
    # hdrs = {"Content-Type": "application/json", "X-Request-Id": "abc"}.
    # Call format_req(*endpoint, timeout=1.5, **hdrs) and print the result.


    # Practice multi-source * unpacking into a variadic function:
    # Define total_with_label(label: str, *nums: int, scale: int = 1) -> str
    # returning f"{label}: {sum(nums) * scale}".
    # Create base_pts = [10, 20, 30] and bonus_pts = (5, 15).
    # Unpack both in a single call: total_with_label("score", *base_pts, *bonus_pts, scale=2)
    # and print the result (expected: "score: 160").


    # Practice merging two keyword dicts at the call site:
    # Create net_opts = {"timeout": 3.0} and trace_hdrs = {"X-Trace": "t-42"}.
    # Unpack both dicts in one format_req call and print the result:
    # format_req(
    #     "GET", "https://api.local",
    #     **net_opts,
    #     **trace_hdrs,
    # )
    #
    # Try uncommenting below to trigger TypeError when two unpacked dicts supply
    # the same keyword key:
    # dup_opts = {"timeout": 9.0}
    # print(format_req(
    #     "GET", "https://api.local",
    #     **net_opts,
    #     **dup_opts,
    # ))


def main() -> None:

    print("=== 1. Positional-only (/) and keyword-only (*) markers ===")
    positional_only_and_keyword_only_markers()

    print("\n=== 2. Variadic *args and **kwargs packing ===")
    variadic_args_and_kwargs_packing()

    print("\n=== 3. Call-site * and ** unpacking ===")
    call_site_unpacking_and_composition()


if __name__ == "__main__":
    main()
