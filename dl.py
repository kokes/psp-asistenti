import json
from urllib.parse import urljoin
import ssl
from urllib.request import urlopen
import lxml.html

ssl._create_default_https_context = ssl._create_unverified_context

base_url = "https://www.psp.cz/sqw/hp.sqw?k=192"
HTTP_TIMEOUT_BASE = 30
HTTP_TIMEOUT = 300

if __name__ == "__main__":
    with urlopen(base_url, timeout=HTTP_TIMEOUT_BASE) as r:
        ht = lxml.html.parse(r).getroot()

    data = []
    for link in ht.cssselect("ul.person-list li span a"):
        print(link)
        person_url = urljoin(base_url, link.attrib["href"])
        with urlopen(person_url, timeout=HTTP_TIMEOUT) as rp:
            htp = lxml.html.parse(rp).getroot()
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
