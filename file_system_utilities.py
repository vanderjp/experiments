import os
from pathlib import Path
from typing import List


def clear_log_directory():
    logFiles: List[str] = os.listdir(get_log_directory())

    for logFile in logFiles:
        os.remove(get_log_directory() / logFile)


def get_log_directory() -> Path:
    return get_project_root_directory() / "logs"


def get_project_root_directory() -> Path:
    return Path(__file__).parent
