#!/usr/bin/env python3
import argparse
import json
import platform
import subprocess
from pathlib import Path
import requests

try:
    from pync import Notifier
except ImportError:
    Notifier = None

DATASET_SLUG = "open-bio-base-complete-sur-les-depenses-de-biologie-medicale-interregimes"
DATASET_URL = f"https://www.data.gouv.fr/api/1/datasets/{DATASET_SLUG}/"
WATCH_YEAR = 2025
STATE_FILE = Path(__file__).with_name("state.json")


def parse_args():
    parser = argparse.ArgumentParser(description="Surveille Open Bio et notifie dès que le dataset 2025 apparaît.")
    parser.add_argument(
        "--year",
        type=int,
        default=WATCH_YEAR,
        help="Année à surveiller dans l'URL de la ressource Open Bio.",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Simuler la détection d'une ressource pour l'année surveillée.",
    )
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Ne pas enregistrer l'état après l'exécution.",
    )
    return parser.parse_args()

def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {"year_available": False, "last_year_resource_ids": []}

def save_state(state):
    STATE_FILE.write_text(json.dumps(state, indent=2))

def fetch_resources(api_url):
    r = requests.get(api_url, timeout=30)
    r.raise_for_status()
    data = r.json()
    return data.get("resources", [])


def extract_year_resources(resources, year):
    year_token = f"Annee={year}"
    matches = []
    for res in resources:
        url = (res.get("url") or "")
        if year_token in url:
            matches.append(res)
    return matches


def _notify_with_osascript(msg):
    escaped = msg.replace("\\", "\\\\").replace('"', '\\"')
    subprocess.run(
        ["osascript", "-e", f'display notification "{escaped}" with title "Veille Open Bio"'],
        check=False,
    )

def notify(msg):
    if Notifier is None:
        _notify_with_osascript(msg)
        return

    try:
        Notifier.notify(msg, title="Veille Open Bio")
    except OSError:
        if platform.system() == "Darwin":
            _notify_with_osascript(msg)
        else:
            print(msg)


def main():
    args = parse_args()
    state = load_state() if not args.test else {"year_available": False, "last_year_resource_ids": []}

    resources = fetch_resources(DATASET_URL)
    year_resources = extract_year_resources(resources, args.year)
    year_ids = {res.get("id") for res in year_resources if res.get("id")}

    if args.test:
        print(f"MODE TEST : surveillance de l'année {args.year} sur le dataset Open Bio.")

    if not year_ids:
        print(f"Pas encore de ressource Open Bio {args.year} détectée.")
        if not args.test and state.get("year_available"):
            state["year_available"] = False
            if not args.no_save:
                save_state(state)
        return

    if not state.get("year_available"):
        notify(f"Open Bio {args.year} est maintenant disponible !")
        print(f"Open Bio {args.year} détecté.")
        state["year_available"] = True

    old_year_ids = set(state.get("last_year_resource_ids", [])) if not args.test else set()
    added = year_ids - old_year_ids
    if added:
        notify(f"Nouvelle ressource Open Bio {args.year} détectée ({len(added)})")
        print("ALERTE:", added)

    if not args.test and not args.no_save:
        state["last_year_resource_ids"] = list(year_ids)
        save_state(state)
    else:
        print("state.json n'a pas été mis à jour.")

if __name__ == "__main__":
    main()
