import argparse
import os
import time
import traceback
import json
import re

from pathlib import Path

from zoti import Zoti
from read_sheet import Drivi

from log import get_logger

log = get_logger(__name__)

regex = re.compile('=HYPERLINK\\("(.*?)","(.*?)"\\)')


def run(config_file: dict,
        dest_path: Path):
    try:
        with open(config_file) as _f:
            config = json.load(_f)

        spreadsheet_id = config['spreadsheet_id']
        library_id = config['library_id']
        library_type = config['library_type']

        d = Drivi()
        zot = Zoti(library_id,
                   library_type)

        stored_items = zot.collection_items()
        ids = map(lambda x: x.get("extra", ""), stored_items)
        ids = filter(lambda x: x is not None and x != "", ids)
        ids = set([*map(lambda x: int(x), ids)])

        refs = d.read_spreadsheet(spreadsheet_id=spreadsheet_id,
                                  range="A2:G")

        breakpoint()
        for ref in refs:
            try:
                id = int(ref[0])

                if id in ids:
                    log.info(
                        f"The reference {ref} is already added to the library")
                    continue

                title = ref[3]

                url = ref[4]
                assert len(url.strip()) > 0, \
                    "url value cannot be empty"

                document = ref[5]
                document = re.search(regex, document)

                ref_info = {
                    "title": title,
                    "url": url,
                    "extra": id
                }

                if document:
                    try:
                        document = document.groups()[0]

                        ref_info["itemType"] = "journalArticle"
                        ref_info["url"] = document
                        ref_info["archive"] = url

                    except Exception:
                        raise AssertionError(f"Malformed doc value at {ref}")
                else:
                    ref_info["itemType"] = "webpage"

                zot.add_reference(ref_info)
            except AssertionError as err:
                log.error(f"We cannot add the ref {ref}")
                log.error(err)
            except Exception:
                log.error(traceback.print_exc())
                raise

    except Exception:
        log.error(traceback.print_exc())
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('-c', '--config_file',
                        help="Config file that contains the collections to query",
                        required=True)
    parser.add_argument('-dp', '--destination_path',
                        help="Destination path for the pipeline assets.",
                        required=True)

    ARGS = parser.parse_args()

    config_file = Path(ARGS.config_file)
    dest_path = Path(ARGS.destination_path)

    assert config_file.exists(), \
        "Config file does not exist"

    if not dest_path.exists():
        log.warning("Destination path does not exist. Making ...")
        dest_path.mkdir(parents=True)

    run(config_file=config_file,
        dest_path=dest_path)
