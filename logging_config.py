from datetime import datetime
from pathlib import Path

from loguru import logger

from file_system_utilities import get_log_directory


def configure_logger():
    logger.remove()

    log_file: Path = get_log_directory() / f"log_{datetime.now().strftime('%m_%d_%Y')}.log"
    logger.add(log_file, rotation="5 MB", enqueue=True)
