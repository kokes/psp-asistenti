import argparse
import json
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

JSON_FILENAME = "asistenti.json"

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", type=int, default=200, help="Pocet stranek ke stazeni")
    args = parser.parse_args()

    with urlopen(base_url, timeout=HTTP_TIMEOUT_BASE) as r:
        ht = lxml.html.parse(r).getroot()

    data = []
    if os.path.exists(JSON_FILENAME):
        with open(JSON_FILENAME, "rt", encoding="utf-8") as f:
            data = json.load(f)

    links = ht.cssselect("ul.person-list li span a")
    random.shuffle(links)
    for link in links[: args.n]:
        print(link.text_content())
        person_url = urljoin(base_url, link.attrib["href"])
        with urlopen(person_url, timeout=HTTP_TIMEOUT) as rp:
            htp = lxml.html.parse(rp).getroot()
        name = htp.cssselect("h1")[0].text.replace("\xa0", " ")
        assistants = [
            j.text_content().replace("\xa0", " ")
            for j in htp.cssselect("ul.assistants li > strong")
        ]
        data = [j for j in data if j["url"] != person_url]
        data.append(
            {
                "poslanec": name,
                "url": person_url,
                "asistenti": sorted(assistants),
            }
        )

    data.sort(key=lambda x: x["url"])
    with open(JSON_FILENAME, "wt", encoding="utf-8") as fw:
        json.dump(data, fw, indent=2, ensure_ascii=False)
