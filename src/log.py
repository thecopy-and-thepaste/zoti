import os
import sys
import logging
import tempfile
import platform


# Verify if system is macOS
foldername = '/tmp' if platform.system() == 'Darwin' else tempfile.gettempdir()
foldername = os.path.join(foldername, 'logs')
if not os.path.exists(foldername):
    os.makedirs(foldername)
FILENAME = "txt_datasets.log"
PATH = os.path.join(foldername, FILENAME)
FORMAT = "%(asctime)s [%(name)-12s] [%(levelname)-5.5s]  %(message)s"
DEFAULT_LEVEL = logging.INFO
logFormatter = logging.Formatter(FORMAT)
logging.basicConfig(stream=sys.stderr, format=FORMAT)


def get_logger(name, path=PATH, level=DEFAULT_LEVEL):
    """Return a logger with the specified name.

    Parameters
    ----------
    name : str
        Name of the logger
    path : str, optional
        Path of the file for logging (default is PATH)
    level : int or str, optional
        Logging level of this logger (default is DEFAULT_LEVEL)

    Returns
    -------
    Logger
        Instance of a logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    filename = path
    fileHandler = logging.FileHandler(filename, mode='a')
    fileHandler.setFormatter(logFormatter)
    logger.addHandler(fileHandler)

    return logger