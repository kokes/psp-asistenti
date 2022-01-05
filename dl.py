import json
from urllib.parse import urljoin
import requests
import lxml.html

base_url = "https://www.psp.cz/sqw/hp.sqw?k=192"
HTTP_TIMEOUT = 30

if __name__ == "__main__":
    r = requests.get(base_url, timeout=HTTP_TIMEOUT)
    r.raise_for_status()

    data = []
    ht = lxml.html.fromstring(r.text)
    for link in ht.cssselect("ul.person-list li span a"):
        person_url = urljoin(base_url, link.attrib["href"])
        rp = requests.get(person_url, timeout=HTTP_TIMEOUT)
        rp.raise_for_status()
        htp = lxml.html.fromstring(rp.text)
        name = htp.cssselect("h1")[0].text.replace("\xa0", " ")
        assistants = [
            j.text_content().replace("\xa0", " ")
            for j in htp.cssselect("ul.assistants li > strong")
        ]
        data.append(
            {
                "poslanec": name,
                "url": person_url,
                "asistenti": sorted(assistants),
            }
        )

    with open("asistenti.json", "wt", encoding="utf-8") as fw:
        json.dump(data, fw, indent=2, ensure_ascii=False)
