"""A script to scrape all online files from Cambridge's Computer Science course"""
 
import re
import os
import json
import urllib3
 
from bs4 import BeautifulSoup
from typing import Dict, List
from dataclasses import dataclass
 
 
BASE_URL = "https://www.cl.cam.ac.uk/teaching/2122/"
PART_URL = BASE_URL + "part{}.html"
 
BASE_PATH = "./files"
EXTS_IGNORE = ("html", "htm", "php")
 
HTTP_POOL = urllib3.PoolManager(
    retries=urllib3.Retry(redirect=5, raise_on_redirect=False)
)
 
TOPIC_REGEX = r"[A-Z][\w\+\-]+(?=/)"
EXT_URL_REGEX = r"https?://(www\.)?([\w\-\~]+/)+\.[a-zA-Z]{1,4}"
INT_URL_REGEX = r"[\.\w\-/\\]+\.[a-zA-Z]{1,4}"
 
 
@dataclass
class Part:
    """A dataclass defining individual parts"""
    proper_name: str
    url_name: str
 
    def __hash__(self):
        return hash(self.url_name)
 
 
@dataclass
class Topic:
    """A dataclass defining individual topics"""
    name: str
    part: Part
    url: str
 
    def __hash__(self):
        return hash(self.name + self.part.proper_name)
 
 
class File_Item:
    """A class defining individual files"""
 
    def __init__(self, url: str, part: Part, topic: Topic):
        """
        params:
            url (str) The fully-qualified url that points to this file
            part (Part) The 'part' of the syllabus this file is under
            topic (Topic) The 'topic' of the syllabus this file is under
        """
 
        self.url = url
        self.part = part
        self.topic = topic
 
        self.local_dir = f"{BASE_PATH}/{part.proper_name}/{topic.name}"
        self.fname = url[url.rfind('/') + 1 :]
 
        self.full_local_path = self.local_dir + '/' + self.fname
 
 
def handle_GET(url: str, obj: Part | Topic | File_Item) -> urllib3.response.HTTPResponse | None:
    """For handling get requests
        params:
            url (str) The fully-qualified URL to GET
            obj (Part | Topic | File_Item) The object to append to `unsuccessful`,
                    if the request does not work
        returns:
            (urllib3.response.HTTPResponse | None) Either the response (on success) or None
    """
 
    try:
        r = HTTP_POOL.request_encode_url("GET", url)
    except urllib3.exceptions.HTTPError as e:
        print(f"[!] Failed to get {url} ({e})")
        unsuccessful.append(obj)
        return None
    else:
        if r.status // 100 == 2:
            return r
        else:
            print(f"[!] Non-200 status on {url} (code {r.status})")
            unsuccessful.append(obj)
            return None
 
 
def get_links(r: urllib3.response.HTTPResponse) -> List[str]:
    """For retrieving URLs from a HTTP(s) response
        params:
            r (urllib3.response.HTTPResponse) The HTTP(s) response
        returns:
            (List[str]) An list of URLs
    """
 
    soup = BeautifulSoup(r.data, "html.parser")
 
    # Ignore indexes
    if soup.title.string.startswith("Index of"):
        return []
 
    a_tags = soup.find_all("a")
    urls = []
    for a in a_tags:
        if "href" in a.attrs:
            urls.append(a.attrs["href"])
            
    return urls
 
 
PARTS = (
    Part("IA", "1a"),
    Part("IB", "1b"),
    Part("II-50", "2-50"),
    Part("II-75", "2-75")
)
 
unsuccessful: List[Part | Topic | File_Item] = []
site: Dict[
    Part, Dict[
        Topic, List[File_Item]
    ]
] = {p: {} for p in PARTS}
 
for part in PARTS:
    print(f"\n[*] Onto part {part.proper_name}\n")
 
    # Get 'part' page
    p_url = PART_URL.format(part.url_name)
    part_resp = handle_GET(p_url, part)
    if part_resp is None:
        continue
 
    all_urls = get_links(part_resp)
 
    # Get topic urls in the part
    topics: List[Topic] = []
    for url in all_urls:
        m = re.match(TOPIC_REGEX, url)
        if m is None:
            continue
        
        topics.append(
            Topic(m.group(), part, BASE_URL + m.group())
        )
    
    # Get file urls in topics
    for topic in topics:
        site[part][topic] = []
 
        for loc in ("materials.html", "slides"):
            topic_materials = handle_GET(topic.url + '/' + loc, topic)
            if topic_materials is None:
                continue
 
            all_urls = get_links(topic_materials)
            for url in all_urls:
                # Check if external file (and not disallowed extension)
                if (
                    re.match(EXT_URL_REGEX, url) is not None and 
                    not any(map(lambda x: url.endswith(x), EXTS_IGNORE))
                ):
                    f = File_Item(url, part, topic)
                    site[part][topic].append(f)
 
                    # Get file
                    file_resp = handle_GET(f.url, f)
                    if file_resp is None:
                        continue
 
                    # Save locally
                    os.makedirs(os.path.dirname(f.full_local_path), exist_ok=True)
                    with open(f.full_local_path, "wb") as f:
                        f.write(file_resp.data)
                # Check if internal file (and not disallowed extension)
                elif (
                    re.match(INT_URL_REGEX, url) is not None and
                    not any(map(lambda x: url.endswith(x), EXTS_IGNORE))
                ):
                    f = File_Item(topic.url + '/' + url, part, topic)
                    site[part][topic].append(f)
 
                    # Get file
                    file_resp = handle_GET(f.url, f)
                    if file_resp is None:
                        
                        continue
 
                    # Save locally
                    os.makedirs(os.path.dirname(f.full_local_path), exist_ok=True)
                    with open(f.full_local_path, "wb") as f:
                        f.write(file_resp.data)
 
 
# Output other stuff
with open(BASE_PATH + "/site.json", "w") as f:
    __site = {}
    # Broken
    quit()
    for part in site.keys():
        _p = part.proper_name
        for topic in site[part].keys():
            _t = topic.name
            for file in site[part]:
                __site[_p][_t][file.name] = vars(file)
 
    json.dump(__site, f)
 
with open(BASE_PATH + "/unsuccessful.txt", "w") as f:
    for i in unsuccessful:
        if type(i) == Part:
            f.write(
                f"Part {i.proper_name}\n"
            )
        elif type(i) == Topic:
            f.write(
                f"Topic {i.name} (in part {i.part.proper_name})\n"
            )
        else:
            f.write(
                f"File {i.fname} (@{i.url}; in part {i.part.proper_name}, topic {i.topic.name})\n"
            )