import os
import time
import traceback

import threading

from pathlib import Path
from typing import List

from pyzotero import zotero
from dotenv import load_dotenv

from utils import barified
from log import get_logger


load_dotenv()

log = get_logger(__name__)


class Zoti:

    def __init__(self,
                 library_id: str,
                 library_type: str) -> None:
        try:
            api_key = os.environ.get("ZOTERO_API_KEY")

            assert api_key is not None and len(api_key) > 0, \
                "ZOTERO_API_KEY not found"

            self.__library_id = library_id
            self.__library_type = library_type

            self.__i = zotero.Zotero(library_id,
                                     library_type,
                                     api_key)
        except Exception:
            log.error(traceback.print_exc())
            raise

    @property
    def i(self):
        try:
            return self.__i
        except Exception:
            log.error(traceback.print_exc())
            raise

    def __is_valid_ref(self,
                       ref: dict):
        try:
            return True
        except Exception:
            log.error(traceback.print_exc())
            raise

    def __total_items(self):
        try:
            return self.__i.count_items()
        except Exception:
            log.error(traceback.print_exc())
            raise

    def __get_items(self,
                    window=50,
                    start=0):
        try:
            items = self.__i.top(limit=window,
                                 start=start)

            return items
        except Exception:
            log.error(traceback.print_exc())
            raise

    def collection_items(self,
                         window=50):
        try:
            total_items = self.__total_items()

            batches = [*range(0, total_items, window)]

            def wrapper(batch_ix, **kwargs):
                try:
                    res = []

                    try:
                        tmp = self.__get_items(window=window,
                                               start=batch_ix)
                    except Exception:
                        log.error(traceback.print_exc())
                        return res

                    res_items = [x['data'] for x in tmp]

                    return res_items

                except Exception:
                    log.error(traceback.print_exc())

            log.info("Fetching collection from Zotero")
            res = barified(wrapper,
                           batches,
                           **{"max_workers": 4})

            res = [x for xx in res for x in xx]

            return res
        except Exception:
            log.error(traceback.print_exc())
            raise

    def is_in_library(self,
                      id: str):
        try:
            items = self.collection_items()

            res = [*map(lambda x: (
                x.get("archive"),
                x.get("url")
            ), items)]
            res = [x for xx in res for x in xx]

            res = set([*filter(lambda x: x is not None or x != "",
                               res)])

            return id in res
        except Exception:
            log.error(traceback.print_exc())
            raise

    def add_reference(self,
                      ref: dict):
        try:
            assert self.__is_valid_ref(ref=ref), \
                "Not valid reference"

            type_ref = ref['itemType']

            try:
                template = self.__i.item_template(type_ref)
            except Exception:
                log.error("Type of reference not valid")
                log.error(traceback.print_exc())
                raise

            template.update(ref)
            resp = self.__i.create_items([template])

            return resp
        except AssertionError:
            raise
        except Exception:
            log.error(traceback.print_exc())
            raise

    def update_documents(self):
        try:
            items = self.collection_items()

            for item in items:
                item_key = item['key']

                children = self.__i.children(item_key, itemType="attachment")

                if len(children) > 1:
                    log.error(f"More than one children on {item}")

                if len(children) == 1:
                    child = children[0]['data']

                    breakpoint()
                    # file = self.__i.file(child['key'])
                    # TODO: Upload
                    new_url = "new_url"
                    new_item = item

                    new_item['archive'] = new_item['url']
                    new_item['url'] = new_url

                    try:
                        was_update = self.__i.update_item(new_item)

                        assert was_update, f"Unknown error at updating {item}"

                        was_deleted = self.__i.delete_item(child)
                    except Exception:
                        log.error(traceback.print_exc())
                        raise

        except Exception:
            log.error(traceback.print_exc())
            raise
