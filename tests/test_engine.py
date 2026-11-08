import pytest

from pyflow import (
    Task, Workflow, WorkflowValidationError, TaskExecutionError,
    TaskStatus, run, format_report,
)


def test_empty_workflow():
    result = run(Workflow())
    assert result.succeeded
    assert result.outputs == {}
    assert result.task_states == {}


def test_order_and_direct_inputs():
    calls = []
    workflow = Workflow()

    def produce(inputs, params):
        calls.append("a")
        assert inputs == {}
        return 4

    def independent(inputs, params):
        calls.append("b")
        return 9

    def consume(inputs, params):
        calls.append("c")
        assert inputs == {"a": 4}
        return inputs["a"] * 2

    workflow.add_task(Task("c", consume, frozenset({"a"})))
    workflow.add_task(Task("b", independent))
    workflow.add_task(Task("a", produce))
    result = run(workflow)
    assert calls == ["a", "b", "c"]
    assert result.outputs == {"a": 4, "b": 9, "c": 8}
    assert result.succeeded


def test_params():
    workflow = Workflow()
    workflow.add_task(Task("task", lambda inputs, params: params["value"] + 1, params={"value": 3}))
    assert run(workflow).outputs["task"] == 4


def test_success_status_and_times():
    workflow = Workflow()
    workflow.add_task(Task("task", lambda inputs, params: "ok"))
    result = run(workflow)
    state = result.task_states["task"]
    assert state.status == TaskStatus.SUCCEEDED
    assert state.started_at is not None
    assert state.finished_at is not None
    assert state.duration >= 0
    assert result.duration >= state.duration


def test_failure_and_skipped_dependents():
    workflow = Workflow()

    def fail(inputs, params):
        raise ValueError("test error")

    workflow.add_task(Task("a", fail))
    workflow.add_task(Task("b", lambda i, p: None, frozenset({"a"})))
    workflow.add_task(Task("c", lambda i, p: None, frozenset({"b"})))
    with pytest.raises(TaskExecutionError) as error:
        run(workflow)
    assert error.value.task_name == "a"
    assert isinstance(error.value.__cause__, ValueError)
    result = error.value.result
    assert not result.succeeded
    assert result.task_states["a"].status == TaskStatus.FAILED
    assert result.task_states["a"].error == "ValueError: test error"
    assert result.task_states["b"].status == TaskStatus.SKIPPED
    assert result.task_states["c"].status == TaskStatus.SKIPPED
    assert result.outputs == {}


def test_independent_task_runs_after_failure():
    workflow = Workflow()

    def fail(inputs, params):
        raise RuntimeError("problem")

    workflow.add_task(Task("a", fail))
    workflow.add_task(Task("b", lambda inputs, params: 7))
    with pytest.raises(TaskExecutionError) as error:
        run(workflow)
    assert error.value.result.outputs == {"b": 7}
    assert error.value.result.task_states["b"].status == TaskStatus.SUCCEEDED


def test_invalid_workflow_does_not_execute():
    workflow = Workflow()
    workflow.add_task(Task("a", lambda i, p: None, frozenset({"missing"})))
    with pytest.raises(WorkflowValidationError):
        run(workflow)


def test_text_report():
    workflow = Workflow()
    workflow.add_task(Task("task", lambda i, p: 1))
    result = run(workflow)
    report = format_report(result)
    assert "task: SUCCEEDED (" in report
    assert "Calkowity czas:" in report
