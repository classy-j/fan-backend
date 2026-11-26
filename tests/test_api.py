"""API tests for the agents that run without an OpenAI key (Oai, Jai, Kai)."""
import shutil

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from app import config, kai_agent, main

SAMPLE_AVAILABILITY = config.BASE_DIR / "data" / "samples" / "availability.csv"


@pytest.fixture()
def client(tmp_path, monkeypatch):
    # Copy writable Kai data into a temp dir so tests don't modify the repo.
    for name in ("ideas.csv", "kudos.csv"):
        shutil.copy(config.DATA_DIR / name, tmp_path / name)
    monkeypatch.setattr(kai_agent, "IDEAS_FILE", tmp_path / "ideas.csv")
    monkeypatch.setattr(kai_agent, "KUDOS_FILE", tmp_path / "kudos.csv")
    monkeypatch.setattr(main, "IDEAS_FILE", tmp_path / "ideas.csv")
    monkeypatch.setattr(main, "KUDOS_FILE", tmp_path / "kudos.csv")
    return TestClient(main.app)


def availability_records():
    df = pd.read_csv(SAMPLE_AVAILABILITY, encoding="utf-8-sig")
    return df, df.to_dict(orient="records")


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_schedule_respects_availability_and_max_hours(client):
    df, records = availability_records()
    res = client.post("/generate_schedule", json={"availability": records})
    assert res.status_code == 200
    schedule = pd.DataFrame(res.json()["schedule"])

    avail = df.set_index("Employee")
    shifts = df.columns[2:]
    for emp in schedule.index:
        for shift in shifts:
            if schedule.loc[emp, shift] == 1:
                assert avail.loc[emp, shift] == 1, f"{emp} scheduled for {shift} while unavailable"
        assert schedule.loc[emp].sum() <= avail.loc[emp, "MaxHoursPerWeek"]
    # at most one person per shift
    assert (schedule.sum(axis=0) <= 1).all()


def test_preview_csv(client):
    with open(SAMPLE_AVAILABILITY, "rb") as f:
        res = client.post("/preview", files={"file": ("availability.csv", f, "text/csv")})
    assert res.status_code == 200
    assert len(res.json()["preview"]) > 0


def test_jai_growth_path(client):
    res = client.get("/jai/growth/101")
    assert res.status_code == 200
    assert "not found" not in res.json()["result"]


def test_jai_unknown_employee(client):
    assert "not found" in client.get("/jai/growth/999999").json()["result"]


def test_kai_submit_and_upvote_idea(client):
    before = len(client.get("/kai/ideas").json()["ideas"])
    client.post("/kai/idea", json={"idea_text": "Test idea", "employee": "Tester", "branch": "Bugis"})
    ideas = client.get("/kai/ideas").json()["ideas"]
    assert len(ideas) == before + 1

    new_id = ideas[-1]["idea_id"]
    assert "Upvoted" in client.post(f"/kai/upvote/{new_id}").json()["result"]


def test_kai_kudos(client):
    before = len(client.get("/kai/kudos_list").json()["kudos"])
    client.post("/kai/kudos", json={"from_emp": "A", "to_emp": "B", "message": "Thanks!"})
    assert len(client.get("/kai/kudos_list").json()["kudos"]) == before + 1
