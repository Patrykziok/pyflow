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

## Przykład

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

Do sprawdzania cykli wykorzystano DFS, a do ustalania kolejności zadań algorytm Kahna z kopcem. Warstwy grupują zadania, których zależności zostały już spełnione.

Dla V zadań i E zależności przejście po grafie ma złożoność O(V + E). Sortowanie nazw i użycie kopca zwiększają koszt do O(V + E + V log V + E log E) w najgorszym przypadku.