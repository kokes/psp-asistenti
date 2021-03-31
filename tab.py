import csv
import json

with open("asistenti.json", "rt", encoding="utf-8") as f:
    data = json.load(f)

with open("asistenti.csv", "wt", encoding="utf-8") as fw:
    cw = csv.writer(fw)
    cw.writerow(["poslanec", "url", "asistent"])
    for poslanec in data:
        for asistent in poslanec["asistenti"] or [None]:
            cw.writerow([poslanec["poslanec"], poslanec["url"], asistent])
