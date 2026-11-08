from time import perf_counter

from .graph import topological_order
from .models import RunResult, TaskState, TaskStatus, Workflow


class TaskExecutionError(RuntimeError):
    def __init__(self, task_name: str, result: RunResult) -> None:
        self.task_name = task_name
        self.result = result
        super().__init__(f"Blad wykonania zadania '{task_name}'")


def run(workflow: Workflow) -> RunResult:
    started_at = perf_counter()
    workflow.validate()
    order = topological_order(workflow)
    states = {name: TaskState() for name in order}
    outputs = {}
    first_failure = None

    for name in order:
        task = workflow.tasks[name]
        state = states[name]

        if any(states[dep].status != TaskStatus.SUCCEEDED for dep in task.dependencies):
            state.status = TaskStatus.SKIPPED
            continue

        inputs = {dep: outputs[dep] for dep in task.dependencies}
        state.status = TaskStatus.RUNNING
        state.started_at = perf_counter()

        try:
            outputs[name] = task.function(inputs, task.params)
        except Exception as exc:
            state.status = TaskStatus.FAILED
            state.error = f"{type(exc).__name__}: {exc}"
            if first_failure is None:
                first_failure = (name, exc)
        else:
            state.status = TaskStatus.SUCCEEDED
        finally:
            state.finished_at = perf_counter()

    result = RunResult(outputs, states, started_at, perf_counter())
    if first_failure is not None:
        task_name, original_error = first_failure
        raise TaskExecutionError(task_name, result) from original_error
    return result


def format_report(result: RunResult) -> str:
    lines = []
    for name, state in result.task_states.items():
        line = f"{name}: {state.status.value} ({state.duration:.6f} s)"
        if state.error is not None:
            line += f" - {state.error}"
        lines.append(line)
    lines.append(f"Calkowity czas: {result.duration:.6f} s")
    return "\n".join(lines)
