import pytest

from pyflow import Task, Workflow, WorkflowValidationError


def work(inputs, params):
    return None


def test_duplicate_task():
    workflow = Workflow()
    workflow.add_task(Task("a", work))
    with pytest.raises(WorkflowValidationError):
        workflow.add_task(Task("a", work))


def test_missing_dependency():
    workflow = Workflow()
    workflow.add_task(Task("a", work, frozenset({"b"})))
    with pytest.raises(WorkflowValidationError, match="b"):
        workflow.validate()


def test_self_dependency():
    with pytest.raises(WorkflowValidationError):
        Task("a", work, frozenset({"a"}))
    with pytest.raises(WorkflowValidationError):
        Task("", work)


def test_cycle():
    workflow = Workflow()
    workflow.add_task(Task("a", work, frozenset({"b"})))
    workflow.add_task(Task("b", work, frozenset({"a"})))
    with pytest.raises(WorkflowValidationError):
        workflow.validate()
