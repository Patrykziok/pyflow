from copy import deepcopy
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Callable, Mapping


class WorkflowValidationError(ValueError):
    """Blad definicji zadania lub grafu workflowu."""


@dataclass(frozen=True)
class Task:
    name: str
    function: Callable[[Mapping[str, Any], Mapping[str, Any]], Any]
    dependencies: frozenset[str] = field(default_factory=frozenset)
    params: Mapping[str, Any] = field(default_factory=dict)
    description: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise WorkflowValidationError("Nazwa zadania nie moze byc pusta.")
        if not callable(self.function):
            raise WorkflowValidationError("Funkcja zadania musi byc wywolywalna.")

        dependencies = frozenset(self.dependencies)
        if self.name in dependencies:
            raise WorkflowValidationError(
                f"Zadanie '{self.name}' nie moze zalezec od samego siebie."
            )

        object.__setattr__(self, "dependencies", dependencies)
        object.__setattr__(
            self, "params", MappingProxyType(deepcopy(dict(self.params)))
        )


class Workflow:
    def __init__(self) -> None:
        self._tasks: dict[str, Task] = {}

    @property
    def tasks(self) -> Mapping[str, Task]:
        return MappingProxyType(self._tasks)

    def add_task(self, task: Task) -> None:
        if task.name in self._tasks:
            raise WorkflowValidationError(
                f"Zadanie o nazwie '{task.name}' juz istnieje."
            )
        self._tasks[task.name] = task

    def validate(self) -> None:
        for task in self._tasks.values():
            for dependency in task.dependencies:
                if dependency not in self._tasks:
                    raise WorkflowValidationError(
                        f"Zadanie '{task.name}' ma nieznana zaleznosc '{dependency}'."
                    )

        visited: set[str] = set()
        visiting: set[str] = set()

        def visit(name: str) -> None:
            if name in visiting:
                raise WorkflowValidationError(
                    f"Wykryto cykl zaleznosci przy zadaniu '{name}'."
                )
            if name in visited:
                return

            visiting.add(name)
            for dependency in sorted(self._tasks[name].dependencies):
                visit(dependency)
            visiting.remove(name)
            visited.add(name)

        for name in sorted(self._tasks):
            visit(name)
