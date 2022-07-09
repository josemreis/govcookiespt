import pandas as pd
import tldextract
import os
import json
import re
import subprocess

# remove social media platforms, app stores, non completely public companies, and private/public associations
DOMAINS_TO_IGNORE_REGEX = "|".join(
    [
        "youtube",
        "twitter",
        "facebook",
        "google",
        "instagram",
        "apple",
        "galp",
        "inatel",
        "endesa",
        "edp",
        "ana",
        "ordem",
        "o(r|t)oc",
        "(\-|\s)S(\.)?(A\.)?",
        "ctt",
        "flickr",
        "linkedin",
        "nos\.pt",
        "goldenergy",
        "meo\.pt",
        "tap\.pt",
        "ajudademae",
    ]
)

# data sources
DATA_SOURCES_DIR = "resources/governmental_websites/interm"
DATA_SOURCES_DICT = {
    "dadosgov": os.path.join(DATA_SOURCES_DIR, "dadosgov.json"),
    "eportugal": os.path.join(DATA_SOURCES_DIR, "eportugal.json"),
    "outros": os.path.join(DATA_SOURCES_DIR, "outros.json"),
}
# path for the dataset
OUTPUT_PATH = "resources/governmental_websites/governmental_websites.json"

def validate_url(_url: str) -> bool:
    """validate a url"""
    if re.search(DOMAINS_TO_IGNORE_REGEX, _url):
        return False
    else:
        regex = re.compile(
            r"^((?:http|ftp)s?(\://))?(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"  # domain...
            r"localhost|"  # localhost...
            r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
            r"(?::\d+)?"  # optional port
            r"(?:/?|[/?]\S+)$",
            re.IGNORECASE,
        )
        return re.match(regex, _url) is not None


def _read_websites_json(path: str) -> dict:
    """read a json file containing gov websites and filter out the ones from app stores or social media/video platforms"""
    with open(path) as f:
        dta = json.load(f)
    out = {}
    for i, d in dta.items():
        if validate_url(str(d.get("url"))):
            if not re.search("^http", d.get("url")):
                d["url"] = "https://" + d.get("url")
            out[i] = d
    return out


def read_websites_json() -> list:
    """wrapper around _read_websites_json which is applied to all json files in resources/governmental_websites/interm"""
    urls_added = set()
    i = 0
    out = {}
    for _source, _file in DATA_SOURCES_DICT.items():
        if _file != OUTPUT_PATH:
            if not os.path.isdir(_file) and "json" in _file:
                with open(_file, "r") as f:
                    websites_dict = _read_websites_json(_file)
                    for _, d in websites_dict.items():
                        parsed_url = ".".join(list(tldextract.extract(d.get("url"))))
                        if parsed_url not in urls_added:
                            out[i] = d
                            urls_added.add(parsed_url)
                            i += 1
    return out


def main() -> None:
    if not os.path.isfile(os.path.join(DATA_SOURCES_DIR, "eportugal.json")):
        subprocess.call("python3 scripts/scrape_eportugal_data.py", shell=True)
    if not os.path.isfile(os.path.join(DATA_SOURCES_DIR, "dadosgov.json")):
        subprocess.call("python3 scripts/make_dados_gov_dataset.py", shell=True)
    dta = read_websites_json()
    with open(OUTPUT_PATH, "w") as f:
        json.dump(dta, f, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    main()
