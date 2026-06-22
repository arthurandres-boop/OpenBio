#!/usr/bin/env python3
import json
import os
from pathlib import Path
import requests
from pync import Notifier

DATASET_SLUG = "open-bio-base-complete-sur-les-depenses-de-biologie-medicale-interregimes"
API_URL = f"https://www.data.gouv.fr/api/1/datasets/{DATASET_SLUG}/"

STATE_FILE = Path(__file__).with_name("state.json")

def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {"last_resource_ids": []}

def save_state(state):
    STATE_FILE.write_text(json.dumps(state, indent=2))

def fetch_resources():
    r = requests.get(API_URL, timeout=30)
    r.raise_for_status()
    data = r.json()
    resources = data.get("resources", [])
    return [res.get("id") for res in resources if res.get("id")]

def notify(msg):
    Notifier.notify(msg, title="Veille Open Bio")

def main():
    current_ids = fetch_resources()
    state = load_state()

    old_ids = set(state.get("last_resource_ids", []))
    new_ids = set(current_ids)

    added = new_ids - old_ids

    if added:
        notify(f"Nouvelle ressource détectée sur Open Bio ({len(added)})")
        print("ALERTE:", added)

    state["last_resource_ids"] = current_ids
    save_state(state)

if __name__ == "__main__":
    main()
