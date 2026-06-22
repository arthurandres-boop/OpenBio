#!/usr/bin/env python3
import json
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from pync import Notifier

URL="https://www.data.gouv.fr/fr/datasets/open-bio-base-complete-sur-les-depenses-de-biologie-medicale-interregimes/"
STATE=Path(__file__).with_name("state.json")

def load():
    if STATE.exists():
        return json.loads(STATE.read_text())
    return {"seen":False}

def save(s):
    STATE.write_text(json.dumps(s))

html=requests.get(URL,timeout=30,headers={"User-Agent":"Mozilla/5.0"}).text
soup=BeautifulSoup(html,"html.parser")
text=soup.get_text(" ",strip=True)
found="2025" in text

st=load()
if found and not st["seen"]:
    Notifier.notify("La base Open Bio 2025 semble disponible !",title="Veille Open Bio")
    print("ALERTE : 2025 détecté")
st["seen"]=found
save(st)
