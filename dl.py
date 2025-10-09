import argparse
import csv
import os
import random
import ssl
from urllib.parse import urljoin
from urllib.request import urlopen

import lxml.html

ssl._create_default_https_context = ssl._create_unverified_context

base_url = "https://www.psp.cz/sqw/hp.sqw?k=192"
HTTP_TIMEOUT_BASE = 30
HTTP_TIMEOUT = 300

CSV_FILENAME = "asistenti.csv"

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", type=int, default=200, help="Pocet stranek ke stazeni")
    args = parser.parse_args()

    with urlopen(base_url, timeout=HTTP_TIMEOUT_BASE) as r:
        ht = lxml.html.parse(r).getroot()

    data = []
    if os.path.exists(CSV_FILENAME):
        with open(CSV_FILENAME, "rt", encoding="utf-8") as f:
            cr = csv.DictReader(f)
            data = list(cr)

    links = ht.cssselect("ul.person-list li span a")
    urls = [urljoin(base_url, j.attrib["href"]) for j in links]
    data = [j for j in data if j["url"] in set(urls)]
    random.shuffle(urls)
    for person_url in urls[: args.n]:
        with urlopen(person_url, timeout=HTTP_TIMEOUT) as rp:
            dt = rp.read().decode("windows-1250")
            htp = lxml.html.fromstring(dt)
        name = htp.cssselect("h1")[0].text.replace("\xa0", " ")
        print(name)
        assistants = [
            j.text_content().replace("\xa0", " ")
            for j in htp.cssselect("ul.assistants li > strong")
        ]
        data = [j for j in data if j["url"] != person_url]
        data.extend(
            {
                "poslanec": name,
                "url": person_url,
                "asistent": assistant,
            }
            # at mame radku i kdyz nema asistenty 
            for assistant in assistants or [""]
        )

    data.sort(key=lambda x: (x["url"], x["asistent"]))
    with open(CSV_FILENAME, "wt", encoding="utf-8") as fw:
        cw = csv.DictWriter(fw, fieldnames=["poslanec", "url", "asistent"])
        cw.writeheader()
        for row in data:
            cw.writerow(row)
