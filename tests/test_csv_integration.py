import json
from pathlib import Path

from pyflow import TaskStatus, run
from examples.csv_to_json import make_workflow


def test_csv_to_json(tmp_path):
    source = Path(__file__).resolve().parents[1] / "examples" / "sample.csv"
    output = tmp_path / "report.json"
    result = run(make_workflow(source, output))
    assert result.succeeded
    assert all(state.status == TaskStatus.SUCCEEDED for state in result.task_states.values())
    assert json.loads(output.read_text(encoding="utf-8")) == {"books": 15, "games": 20}
    assert result.outputs["save_json"] == str(output)
