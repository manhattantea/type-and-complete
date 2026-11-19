# python 730_runtime_inspection_and_signatures.py

from dataclasses import dataclass
from functools import wraps
import inspect
from typing import Annotated, Any, get_args, get_origin, get_type_hints


def inspecting_signatures_and_parameter_empty() -> None:

    # Ever wondered how FastAPI, Typer, or Pydantic inspect a plain Python
    # function and immediately know which parameters are required, which are
    # keyword-only, and what defaults they carry? They call inspect.signature.
    #
    # inspect.signature(fn) builds a Signature object whose .parameters is an
    # ordered mapping of inspect.Parameter records. Each Parameter exposes
    # .name, .default, .annotation, and .kind (such as POSITIONAL_ONLY,
    # POSITIONAL_OR_KEYWORD, KEYWORD_ONLY, VAR_POSITIONAL, or VAR_KEYWORD).
    #
    # Watch out for the #1 sentinel trap: NEVER write if param.default is None:
    # to check whether a parameter is required!
    #
    #     Suppose def connect(host: str, token: str | None = None) -> None:
    #     - host has NO default, so param.default is inspect.Parameter.empty.
    #     - token HAS a default whose value happens to be None, so
    #       param.default is None!
    #     Checking param.default is None gets BOTH parameters backward. Always
    #     test param.default is inspect.Parameter.empty to detect omitted
    #     defaults (and param.annotation is inspect.Parameter.empty for missing
    #     type annotations).

    def sample_endpoint(host: str, token: str | None = None) -> str:

        return f"{host}:{token}"

    sig = inspect.signature(sample_endpoint)
    print("Starter signature:", sig)

    # Loop over sig.parameters.values() for sample_endpoint and print each
    # parameter's name, kind.name, required flag
    # (param.default is inspect.Parameter.empty), and raw param.default.
    # Confirm host is required while token is optional with default None.


    # Define a function exercising multiple parameter kinds:
    # def fetch_page(url: str, /, *, timeout: float = 5.0, proxy: str | None = None) -> str:
    # returning f"{url} timeout={timeout} proxy={proxy}".
    # Write a helper def summarize_params(fn: Any) -> list[tuple[str, str, bool]]:
    # returning (p.name, p.kind.name, p.default is inspect.Parameter.empty) for
    # every parameter in inspect.signature(fn).parameters.values(). Print the
    # summary for fetch_page.


    # Verify the same sentinel rule for missing annotations:
    # define def untyped(a, b=None): returning (a, b), inspect its signature,
    # and print (p.name, p.annotation is inspect.Parameter.empty, p.default is inspect.Parameter.empty)
    # for each parameter.


def binding_arguments_with_sig_bind() -> None:

    # Re-implementing Python's positional, keyword, and default argument rules
    # by hand is error-prone. Instead, sig.bind(*args, **kwargs) maps incoming
    # arguments to their declared parameter names using CPython's exact call
    # protocol—raising TypeError on missing required arguments, duplicate
    # bindings, or unexpected keyword names before the function body ever runs.
    #
    #     Suppose def send_alert(target: str, retries: int = 3, *, urgent: bool = False):
    #     Calling bound = sig.bind("ops-room", urgent=True) sets
    #     bound.arguments to {"target": "ops-room", "urgent": True}.
    #     Then calling bound.apply_defaults() fills in every omitted default so
    #     bound.arguments becomes {"target": "ops-room", "retries": 3, "urgent": True}.
    #
    # When a framework injects some arguments later (like dependency injection),
    # sig.bind_partial(...) binds only the arguments supplied so far without
    # failing on still-missing required parameters.

    def send_alert(target: str, retries: int = 3, *, urgent: bool = False) -> str:

        return f"{target} retries={retries} urgent={urgent}"

    alert_sig = inspect.signature(send_alert)
    bound_demo = alert_sig.bind("ops-room", urgent=True)
    print("Starter bound.arguments before apply_defaults:", dict(bound_demo.arguments))

    # Call bound_demo.apply_defaults() and print dict(bound_demo.arguments) to
    # confirm retries=3 was populated automatically. Then invoke
    # send_alert(*bound_demo.args, **bound_demo.kwargs) and print the result.


    # Verify sig.bind enforces Python's call protocol:
    # - Inside try / except TypeError as err:, call alert_sig.bind(retries=5)
    #   (missing required target) and print the TypeError message.
    # - Inside a second try / except TypeError as err:, call
    #   alert_sig.bind("ops-room", unknown=1) and print the TypeError message.


    # Test partial binding: call partial = alert_sig.bind_partial(urgent=True),
    # print dict(partial.arguments), then call partial.apply_defaults() and
    # inspect which keys are present while required target remains unbound.


def annotated_metadata_and_range_validation() -> None:

    # typing.Annotated[T, meta1, meta2] attaches arbitrary runtime metadata
    # objects onto a type hint while static type checkers treat Annotated[int, ...]
    # as plain int.
    #
    # Two subtle rules keep runtime hint extraction from failing silently:
    # - Prefer get_type_hints(fn, include_extras=True) over reading raw
    #   param.annotation, because get_type_hints resolves string forward
    #   references (such as files using from __future__ import annotations).
    # - NEVER omit include_extras=True! Calling plain get_type_hints(fn)
    #   silently strips every Annotated wrapper and hands back bare int.
    #
    # Once you have a resolved hint, test get_origin(hint) is Annotated and
    # unpack base_type, *extras = get_args(hint). Compute both inspect.signature
    # and get_type_hints ONCE at decoration time instead of on every call.

    SampleHint = Annotated[int, "demo_meta"]
    print("Starter Annotated origin/args:", get_origin(SampleHint), get_args(SampleHint))

    # Define an immutable metadata descriptor:
    # @dataclass(frozen=True)
    # class ValueRange: with lo: int and hi: int.


    # Write a runtime validator decorator def validate_ranges(fn: Any) -> Any:
    # - Capture sig = inspect.signature(fn) and
    #   hints = get_type_hints(fn, include_extras=True) once at decoration time.
    # - Decorate an inner wrapper with @wraps(fn) so inspect.signature(wrapped)
    #   still reports the original parameters instead of generic varargs.
    # - Inside the wrapper, run bound = sig.bind(*args, **kwargs) followed by
    #   bound.apply_defaults().
    # - For each name, value in bound.arguments.items(): look up
    #   hint = hints.get(name). When get_origin(hint) is Annotated, unpack
    #   base_type, *meta = get_args(hint). For each item in meta: if
    #   isinstance(item, ValueRange), verify isinstance(value, int) and
    #   not isinstance(value, bool) (raising TypeError otherwise) and raise
    #   ValueError(f"{name}={value} outside [{item.lo}, {item.hi}]") if
    #   not (item.lo <= value <= item.hi).
    # - Return fn(*args, **kwargs).


    # Decorate def set_volume(level: Annotated[int, ValueRange(0, 100)], muted: bool = False) -> str:
    # with @validate_ranges, returning f"volume={level} (muted={muted})".
    # Call set_volume(75) and set_volume(level=0, muted=True), and print
    # inspect.signature(set_volume) to confirm @wraps preserved the signature.


    # Verify failure paths and the include_extras trap:
    # - Call set_volume(150) inside try / except ValueError as err: and print err.
    # - Call set_volume(True) inside try / except TypeError as err: and print err.
    # - Print get_type_hints(set_volume) alongside
    #   get_type_hints(set_volume, include_extras=True) to witness ValueRange
    #   disappear when include_extras=True is omitted.


def main() -> None:

    print("=== 1. Inspecting signatures and Parameter.empty ===")
    inspecting_signatures_and_parameter_empty()

    print("\n=== 2. Binding arguments with sig.bind ===")
    binding_arguments_with_sig_bind()

    print("\n=== 3. Annotated metadata and range validation ===")
    annotated_metadata_and_range_validation()


if __name__ == "__main__":
    main()
