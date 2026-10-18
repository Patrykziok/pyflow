# PyFlow - Laboratorium 1

## Instalacja

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

## Testy

```powershell
.\.venv\Scripts\python.exe -m pytest
```

## Przykład workflowu

```python
from pyflow import Task, Workflow, topological_order, execution_layers


def work(inputs, params):
    return None


workflow = Workflow()
workflow.add_task(Task("extract", work))
workflow.add_task(Task("clean_a", work, frozenset({"extract"})))
workflow.add_task(Task("clean_b", work, frozenset({"extract"})))
workflow.add_task(Task("report", work, frozenset({"clean_a", "clean_b"})))

workflow.validate()
print(topological_order(workflow))
print(execution_layers(workflow))
```

## Algorytm i złożoność

Walidacja cykli: DFS, O(V + E).
Sortowanie topologiczne: algorytm Kahna z kopcem, O(E + V log V).
Warstwy wykonania: sortowanie gotowych zadań, O(E + V log V).
V - liczba zadań, E - liczba zależności.
