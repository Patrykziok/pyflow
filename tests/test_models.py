import pytest

from pyflow import Task, Workflow, WorkflowValidationError


def work(inputs, params):
    return inputs, params


def test_empty_workflow_is_valid():
    Workflow().validate()


def test_single_task_is_valid():
    workflow = Workflow()
    workflow.add_task(Task("start", work))
    workflow.validate()
    assert "start" in workflow.tasks


def test_duplicate_task_is_rejected():
    workflow = Workflow()
    workflow.add_task(Task("start", work))
    with pytest.raises(WorkflowValidationError, match="juz istnieje"):
        workflow.add_task(Task("start", work))


def test_empty_name_is_rejected():
    with pytest.raises(WorkflowValidationError, match="pusta"):
        Task(" ", work)


def test_self_dependency_is_rejected():
    with pytest.raises(WorkflowValidationError, match="samego siebie"):
        Task("start", work, frozenset({"start"}))


def test_missing_dependency_is_rejected():
    workflow = Workflow()
    workflow.add_task(Task("report", work, frozenset({"missing"})))
    with pytest.raises(WorkflowValidationError, match="missing"):
        workflow.validate()


def test_cycle_is_rejected():
    workflow = Workflow()
    workflow.add_task(Task("a", work, frozenset({"b"})))
    workflow.add_task(Task("b", work, frozenset({"a"})))
    with pytest.raises(WorkflowValidationError, match="cykl"):
        workflow.validate()


def test_input_params_are_copied():
    params = {"options": [1, 2]}
    task = Task("start", work, params=params)
    params["options"].append(3)
    assert task.params["options"] == [1, 2]


def test_dependencies_are_copied():
    dependencies = {"source"}
    task = Task("other", work, dependencies=dependencies)
    dependencies.add("changed")
    assert task.dependencies == frozenset({"source"})
