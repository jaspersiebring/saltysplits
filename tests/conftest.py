import pytest
import requests
import pathlib
from lxml.etree import Element

# names come from livesplit-core/tests/run_files/mod.rs
LSS_DIR = pathlib.Path(__file__).parent / "run_files"


def drop_empty_tags(element: Element, top_level=True) -> None:
    """Removes empty XML tags from a given LXML ElementTree

    Args:
        element (Element): Root XML element from which empty elements should be removed
        top_level (bool, optional): Whether to only check direct children or all children (recursively)
    """
    # dropping empty tags before comparison, no way to catch that AND actually optional elements (e.g. real_time and/or game_time)
    children = list(element) if top_level else list(element.iter())
    for child in children:
        if len(child) == 0 and not child.text and not child.attrib:
            parent = child.getparent()
            if parent is not None:
                parent.remove(child)


def get_run_files(lss_dir: pathlib.Path) -> None:
    api_url = "https://api.github.com/repos/LiveSplit/livesplit-core/contents/tests/run_files"
    response = requests.get(api_url)
    files = response.json()

    lss_files = [file for file in files if file["name"].endswith(".lss")]
    for lss_file in lss_files:
        lss_src = lss_file["download_url"]
        lss_dst = lss_dir / lss_file["name"]

        if lss_dst.exists() and lss_dst.stat().st_size == lss_file["size"]:
            continue

        with requests.get(lss_src, stream=True) as response:
            response.raise_for_status()
            with open(lss_dst, "w", encoding="utf-8") as file:
                file.write(response.text)


@pytest.fixture
def LIVESPLIT_1_7_0():
    return LSS_DIR / "Grand Theft Auto Vice City - Any% (No SSU).lss"


@pytest.fixture
def LIVESPLIT_1_3():
    return LSS_DIR / "livesplit1.5.lss"
