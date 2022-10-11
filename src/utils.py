import collections
import multiprocessing
import traceback

from tqdm import tqdm
from typing import Callable, List
from concurrent.futures import ThreadPoolExecutor

from log import get_logger

log = get_logger(__name__)

NUM_PROCESSES = multiprocessing.cpu_count() - 2


def barified(func: Callable,
             data: collections.Sized,
             *args,
             **kwargs) -> List:
    """
    Ordered version to parallelize tasks using PoolExecutor and provide a bar
    for estimated time of completion.

    The data is splitted in items and send to a function with signature
    func(item, *args, **kwargs).


    Parameters
    ----------
    func : Callable
        Function to execute for each item in the data collection
    data : collections.Sized
        Data to process, should contains the len method (collections.Sized)

    Returns
    -------
    [List]
        [List of the results of func function]
    """
    try:
        assert isinstance(data, collections.Sized), \
            (f"The object to barify should be a Sized collection and implement the "
             f"`len` method")

        max_workers = kwargs.get('max_workers', NUM_PROCESSES)
        processes_results = []

        with tqdm(total=len(data)) as pbar:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                try:
                    for result in executor.map(lambda x: func(x, *args, **kwargs), data):
                        processes_results.append(result)
                        pbar.update(1)
                except Exception:
                    log.error(traceback.print_exc())
                    raise

        return processes_results
    except Exception as ex:
        raise
