import sys
from datetime import datetime
from pathlib import Path
from time import time

from loguru import logger

import file_system_utilities


def configure_logger(is_delete_existing: bool = True):
    if is_delete_existing:
        file_system_utilities.clear_log_directory()

    logger.remove()

    log_file: Path = file_system_utilities.get_log_directory() / \
                     f"log_{datetime.now().strftime('%m_%d_%Y')}.log"
    logger.add(log_file, rotation="5 MB", enqueue=True)


def format_duration_string(duration: float) -> str:
    minutes: float = round(duration / 60)
    seconds: float = round(duration % 60, 1)

    duration_str: str = f"{seconds}s"

    if minutes > 0:
        duration_str = f"{minutes}m " + duration_str

    return duration_str


def get_final_summary(start_time: float, total_jobs: int) -> str:
    print_eta(total_jobs, start_time, total_jobs)
    job_duration: float = time() - start_time

    duration_str = f"Batch processing completed in {format_duration_string(job_duration)}"
    logger.success(duration_str)
    return duration_str


def print_eta(job_count: int, start_time: time, total_jobs: int):
    duration: float = time() - start_time

    eta: float = (duration / job_count) * (total_jobs - job_count)

    format_duration_string(eta)

    sys.stdout.write(f"\rTasks Completed: {job_count}/{total_jobs} -- "
                     f"Percent Completion: {round((job_count / total_jobs) * 100)}% -- "
                     f"Duration: {format_duration_string(duration)} -- "
                     f"Completion ETA: {format_duration_string(eta)}")
    sys.stdout.flush()
