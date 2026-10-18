from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any, Callable, Mapping


class WorkflowValidationError(ValueError):
    pass


@dataclass
class Task:
    name: str
    function: Callable[[Mapping[str, Any], Mapping[str, Any]], Any]
    dependencies: frozenset[str] = field(default_factory=frozenset)
    params: Mapping[str, Any] = field(default_factory=dict)
    description: str | None = None

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise WorkflowValidationError("Nazwa zadania nie moze byc pusta")

        self.dependencies = frozenset(self.dependencies)
        if self.name in self.dependencies:
            raise WorkflowValidationError("Zadanie nie moze zalezec od samego siebie")

        self.params = deepcopy(dict(self.params))


class Workflow:
    def __init__(self) -> None:
        self.tasks: dict[str, Task] = {}

    def add_task(self, task: Task) -> None:
        if task.name in self.tasks:
            raise WorkflowValidationError(f"Zadanie '{task.name}' juz istnieje")
        self.tasks[task.name] = task

    def validate(self) -> None:
        for name, task in self.tasks.items():
            for dependency in task.dependencies:
                if dependency not in self.tasks:
                    raise WorkflowValidationError(
                        f"Brak zaleznosci '{dependency}' dla zadania '{name}'"
                    )

        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(name: str) -> None:
            if name in visiting:
                raise WorkflowValidationError(f"Wykryto cykl przy zadaniu '{name}'")
            if name in visited:
                return

            visiting.add(name)
            for dependency in self.tasks[name].dependencies:
                visit(dependency)
            visiting.remove(name)
            visited.add(name)

        for name in self.tasks:
            visit(name)
