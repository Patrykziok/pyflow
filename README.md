# PyFlow - Laboratorium 1

PyFlow to prosty model workflowu (grafu zadan i ich zaleznosci). Laboratorium 1 implementuje model `Task`, kontener `Workflow`, walidacje DAG, porzadek topologiczny i warstwy wykonania. Nie uruchamia jeszcze funkcji zadan.

## Wymagania

- Python 3.11 lub nowszy
- Git

## Instalacja (Windows PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

## Testy

```powershell
.\.venv\Scripts\python.exe -m pytest
```

## Przyklad

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

Wyniki:

```text
['extract', 'clean_a', 'clean_b', 'report']
[['extract'], ['clean_a', 'clean_b'], ['report']]
```

## Algorytm i zlozonosc

Walidacja brakujacych zaleznosci oraz wykrywanie cykli jest realizowane za pomoca przeszukiwania DFS. Plan topologiczny powstaje za pomoca algorytmu Kahna z kolejka priorytetowa (kopcem), aby zapewnic alfabetyczna, powtarzalna kolejnosc zadan. Warstwy powstaja z kolejnych grup wezlow o stopniu wejsciowym 0.

Dla V zadan i E zaleznosci: sprawdzanie zaleznosci i DFS maja zlozonosc O(V + E), a sortowanie nazw w walidacji dodaje koszt O(V log V + E log E) w pesymistycznym przypadku. Sortowanie topologiczne ma koszt O(V + E + V log V) po walidacji (kopiec), a wyznaczanie warstw O(V + E + V log V) po walidacji (sortowanie grup). Pamiec pomocnicza O(V + E).
