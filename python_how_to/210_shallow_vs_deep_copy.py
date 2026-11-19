# python 210_shallow_vs_deep_copy.py

import copy
from typing import Any


def shallow_copy_and_shared_children() -> None:

    # Because Python containers store references to heap objects rather than
    # inline values, copying a container always raises one question: do you
    # want a new outer container pointing to the same inner objects, or a full
    # recursive clone of the entire object graph?
    #
    # A shallow copy (dict.copy(), list.copy(), x[:], or copy.copy(x)) allocates
    # a brand-new outer container and copies only the top-level references.
    # That is fast and completely safe when every inner value is immutable
    # (int, str, tuple of ints), but dangerous when inner values are mutable.
    #
    #     Suppose state = {"player": "Ada", "inventory": ["sword"]}.
    #     shallow = state.copy() creates a new dict (shallow is not state),
    #     but shallow["inventory"] is state["inventory"] is STILL True!
    #     Appending to shallow["inventory"] mutates state["inventory"] too.

    starter: dict[str, Any] = {"hp": 100, "tags": ["starter"]}
    shallow_starter = copy.copy(starter)
    print("New outer dict:", shallow_starter is not starter)

    # Observe shallow-copy leakage on a nested list:
    # create state: dict[str, Any] = {"player": "Ada", "inventory": ["sword", "shield"]}.
    # Make shallow_state = state.copy(), append "potion" to
    # shallow_state["inventory"], and print state["inventory"],
    # shallow_state["inventory"], and shallow_state["inventory"] is state["inventory"].


    # Contrast top-level rebinding vs. nested mutation on shallow_state:
    # assign shallow_state["player"] = "Grace" (rebinds a key in the new outer
    # dict) and print state["player"] alongside shallow_state["player"] to see
    # why top-level key replacement stays isolated while inner list mutation leaks.


def deep_copy_and_graph_isolation() -> None:

    # copy.deepcopy(x) recursively traverses the object graph, allocating fresh
    # copies of both the outer container and every nested mutable object inside.
    # Immutable leaf objects (like ints and strings) do not need cloning, so
    # deepcopy safely reuses them.
    #
    #     Suppose nested = [[1, 2], [3, 4]] and clone = copy.deepcopy(nested).
    #     clone is not nested AND clone[0] is not nested[0]. Mutating
    #     clone[0].append(99) leaves nested completely untouched.

    nested: list[list[int]] = [[1, 2], [3, 4]]
    isolated = copy.deepcopy(nested)
    isolated[0].append(99)
    print("Original nested untouched:", nested, "Deep clone:", isolated)

    # Deep-copy a rich game state and prove full isolation:
    # create state: dict[str, Any] = {"player": "Ada", "inventory": ["sword", "shield"]}.
    # Make deep_state = copy.deepcopy(state), append "elixir" to
    # deep_state["inventory"], and print state["inventory"],
    # deep_state["inventory"], and deep_state["inventory"] is state["inventory"].


    # Observe how deepcopy preserves shared structure (DAG aliasing) INSIDE a
    # single graph: create shared = [1, 2] and pair = [shared, shared].
    # Clone with pair_copy = copy.deepcopy(pair) and print
    # pair_copy[0] is pair_copy[1] (True: deepcopy keeps internal sharing!) and
    # pair_copy[0] is shared (False: isolated from the original).


def cycle_memoization_and_custom_hooks() -> None:

    # How does copy.deepcopy(x) preserve internal sharing AND survive
    # self-referential cycles without crashing with RecursionError?
    # Internally, deepcopy passes a memo: dict[int, Any] mapping id(original)
    # to its already-allocated clone. The moment deepcopy visits an object
    # whose id() is already in memo, it returns that cached clone immediately.
    #
    # User-defined classes can customize copying by implementing __copy__(self)
    # and __deepcopy__(self, memo: dict[int, Any]):
    # - Always register memo[id(self)] = clone BEFORE recursively calling
    #   copy.deepcopy(self.tasks, memo) on child fields so cycles work cleanly.
    # - This lets you deep-copy mutable state while keeping a shared reference
    #   to an external resource (like a logger or config handle).

    shared_log: list[str] = ["boot"]
    print("Starter shared log id:", id(shared_log))

    # Prove deepcopy handles a self-referential cycle safely:
    # create cycle: list[Any] = [1, 2] and append it to itself with
    # cycle.append(cycle). Clone it with cloned_cycle = copy.deepcopy(cycle),
    # then print cloned_cycle, cloned_cycle is not cycle (True), and
    # cloned_cycle[2] is cloned_cycle (True).


    # Implement custom copy hooks on a small class right here:
    # define class Worker: storing self.name: str, self.tasks: list[str], and
    # self.logger: list[str] (a shared log list).
    # Implement __deepcopy__(self, memo: dict[int, Any]) -> Worker: that creates
    # clone = Worker(self.name, [], self.logger), registers memo[id(self)] = clone
    # FIRST, then sets clone.tasks = copy.deepcopy(self.tasks, memo) and returns
    # clone. Deep-copy a Worker instance and verify clone.tasks is not
    # original.tasks while clone.logger is original.logger.


def main() -> None:

    print("=== 1. Shallow copy and shared children ===")
    shallow_copy_and_shared_children()

    print("\n=== 2. Deep copy and graph isolation ===")
    deep_copy_and_graph_isolation()

    print("\n=== 3. Cycle memoization and custom hooks ===")
    cycle_memoization_and_custom_hooks()


if __name__ == "__main__":
    main()
