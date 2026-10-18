import pytest

from pyflow import (
    Task,
    Workflow,
    WorkflowValidationError,
    execution_layers,
    topological_order,
)


def work(inputs, params):
    return inputs, params


def test_empty_graph():
    workflow = Workflow()
    assert topological_order(workflow) == []
    assert execution_layers(workflow) == []


def test_single_node():
    workflow = Workflow()
    workflow.add_task(Task("one", work))
    assert topological_order(workflow) == ["one"]
    assert execution_layers(workflow) == [["one"]]


def test_chain():
    workflow = Workflow()
    workflow.add_task(Task("c", work, frozenset({"b"})))
    workflow.add_task(Task("a", work))
    workflow.add_task(Task("b", work, frozenset({"a"})))
    assert topological_order(workflow) == ["a", "b", "c"]
    assert execution_layers(workflow) == [["a"], ["b"], ["c"]]


def test_independent_tasks_in_alphabetical_order():
    workflow = Workflow()
    workflow.add_task(Task("z", work))
    workflow.add_task(Task("a", work))
    assert topological_order(workflow) == ["a", "z"]
    assert execution_layers(workflow) == [["a", "z"]]


def test_parallel_layers():
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
    assert topological_order(workflow) == [
        "extract", "clean_a", "clean_b", "report"
    ]


def test_deterministic_order_independent_of_insertion():
    first = Workflow()
    second = Workflow()
    for name in ["c", "a", "b"]:
        first.add_task(Task(name, work))
    for name in ["b", "c", "a"]:
        second.add_task(Task(name, work))
    assert topological_order(first) == topological_order(second) == ["a", "b", "c"]


def test_topological_order_fails_for_cycle():
    workflow = Workflow()
    workflow.add_task(Task("a", work, frozenset({"b"})))
    workflow.add_task(Task("b", work, frozenset({"a"})))
    with pytest.raises(WorkflowValidationError, match="cykl"):
        topological_order(workflow)


def test_layers_fail_for_missing_dependency():
    workflow = Workflow()
    workflow.add_task(Task("a", work, frozenset({"missing"})))
    with pytest.raises(WorkflowValidationError, match="missing"):
        execution_layers(workflow)
