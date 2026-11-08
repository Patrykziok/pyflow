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

## Laboratorium 2

Funkcja zadania ma postać `function(inputs, params)`.
`inputs` zawiera wyniki bezpośrednich zależności, a `params` to parametry zadania.
Silnik wykonuje zadania synchronicznie, w kolejności topologicznej.

Przykład:

```python
from pyflow import Task, Workflow, run, format_report

def add(inputs, params):
    return params["value"] + 1

workflow = Workflow()
workflow.add_task(Task("a", add, params={"value": 2}))
result = run(workflow)
print(result.outputs)
print(format_report(result))
```

`RunResult` udostępnia `outputs`, `task_states`, `succeeded` i `duration`.
Statusy: `PENDING`, `RUNNING`, `SUCCEEDED`, `FAILED`, `SKIPPED`.
`TaskState` przechowuje status, czasy rozpoczęcia i zakończenia, czas trwania oraz błąd.
Pomiar czasu wykorzystuje `time.perf_counter()`.

Polityka błędów: niezależne zadania są wykonywane mimo błędu innego zadania.
Zadanie zakończone błędem ma status `FAILED`, a zależne od niego `SKIPPED`.
Po zakończeniu przebiegu silnik zgłasza `TaskExecutionError` z nazwą zadania,
oryginalnym wyjątkiem jako przyczyną i wynikiem w `error.result`.
Raport tekstowy tworzy `format_report(result)`; można go również wywołać
na `error.result` po nieudanym przebiegu.

## Przykład CSV -> JSON

```powershell
.\.venv\Scripts\python.exe examples\csv_to_json.py
```

Program odczytuje `examples/sample.csv`, odrzuca błędne lub ujemne wartości,
sumuje kwoty według kategorii i zapisuje `examples/report.json`.
Wyświetla też raport z czasami wykonania kroków i całego przebiegu.
