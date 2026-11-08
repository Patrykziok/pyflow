import csv
import json
from pathlib import Path

from pyflow import Task, Workflow, format_report, run


def read_csv(inputs, params):
    with open(params["path"], encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def clean_rows(inputs, params):
    cleaned = []
    for row in inputs["read_csv"]:
        try:
            amount = int(row["amount"])
        except ValueError:
            continue
        if amount >= 0:
            cleaned.append({"category": row["category"], "amount": amount})
    return cleaned


def aggregate(inputs, params):
    totals = {}
    for row in inputs["clean_rows"]:
        category = row["category"]
        totals[category] = totals.get(category, 0) + row["amount"]
    return dict(sorted(totals.items()))


def save_json(inputs, params):
    path = Path(params["path"])
    with path.open("w", encoding="utf-8") as file:
        json.dump(inputs["aggregate"], file, indent=2, ensure_ascii=False)
    return str(path)


def make_workflow(csv_path, json_path):
    workflow = Workflow()
    workflow.add_task(Task("read_csv", read_csv, params={"path": str(csv_path)}))
    workflow.add_task(Task("clean_rows", clean_rows, frozenset({"read_csv"})))
    workflow.add_task(Task("aggregate", aggregate, frozenset({"clean_rows"})))
    workflow.add_task(Task("save_json", save_json, frozenset({"aggregate"}), {"path": str(json_path)}))
    return workflow


if __name__ == "__main__":
    folder = Path(__file__).resolve().parent
    result = run(make_workflow(folder / "sample.csv", folder / "report.json"))
    print(format_report(result))
