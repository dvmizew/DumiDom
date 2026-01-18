import json
from typing import List, Dict


def load_spider(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
