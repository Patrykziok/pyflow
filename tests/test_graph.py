from pyflow import Task, Workflow, topological_order, execution_layers


def work(inputs, params):
    return None


def test_empty_graph():
    workflow = Workflow()
    assert topological_order(workflow) == []
    assert execution_layers(workflow) == []


def test_single_task():
    params = {"numbers": [1, 2]}
    dependencies = set()
    task = Task("a", work, dependencies, params)
    params["numbers"].append(3)
    dependencies.add("b")
    assert task.params["numbers"] == [1, 2]
    assert task.dependencies == frozenset()

    workflow = Workflow()
    workflow.add_task(task)
    assert topological_order(workflow) == ["a"]
    assert execution_layers(workflow) == [["a"]]


def test_chain():
    workflow = Workflow()
    workflow.add_task(Task("c", work, frozenset({"b"})))
    workflow.add_task(Task("b", work, frozenset({"a"})))
    workflow.add_task(Task("a", work))
    assert topological_order(workflow) == ["a", "b", "c"]


def test_independent_tasks():
    workflow = Workflow()
    workflow.add_task(Task("b", work))
    workflow.add_task(Task("a", work))
    assert topological_order(workflow) == ["a", "b"]


def test_deterministic_order():
    first = Workflow()
    second = Workflow()
    for name in ("c", "a", "b"):
        first.add_task(Task(name, work))
    for name in ("b", "c", "a"):
        second.add_task(Task(name, work))
    assert topological_order(first) == topological_order(second) == ["a", "b", "c"]


def test_execution_layers():
    workflow = Workflow()
    workflow.add_task(Task("report", work, frozenset({"clean_a", "clean_b"})))
    workflow.add_task(Task("clean_b", work, frozenset({"extract"})))
    workflow.add_task(Task("extract", work))
    workflow.add_task(Task("clean_a", work, frozenset({"extract"})))

    assert execution_layers(workflow) == [
        ["extract"],
        ["clean_a", "clean_b"],
        ["report"],
    ]
