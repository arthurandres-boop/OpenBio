# Veille Open Bio

Installation:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python check_open_bio.py
```

Créer le dossier `~/Library/LaunchAgents` si besoin puis copier `launchd.plist`
en remplaçant PATH_TO_PROJECT et PATH_TO_PYTHON.
Charger:
```bash
launchctl load ~/Library/LaunchAgents/fr.openbio.watch.plist
```
