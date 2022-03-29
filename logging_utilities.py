import sys
from datetime import datetime
from pathlib import Path
from time import time

import colorama
from loguru import logger

import file_system_utilities


def get_magenta_string(a_string: str) -> str:
    return f"{colorama.Fore.MAGENTA}{a_string}{colorama.Fore.RESET}"


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

    duration_str = f"Batch processing completed in " \
                   f"{get_magenta_string(format_duration_string(job_duration))}"
    logger.success(duration_str)
    return duration_str


def print_eta(job_count: int, start_time: time, total_jobs: int):
    duration: float = time() - start_time
    duration_str: str = format_duration_string(duration).rjust(8)
    eta: float = (duration / job_count) * (total_jobs - job_count)
    eta_str: str = format_duration_string(eta).rjust(10)
    percent_completion: str = f"{round((job_count / total_jobs) * 100)}%".rjust(4)
    spacer: str = " -- "
    tasks_completed: str = f"{str(job_count).rjust(6)} / {str(total_jobs).rjust(6)}"

    sys.stdout.write(f"\rTasks Completed: {get_magenta_string(tasks_completed)}{spacer}"
                     f"Percent Completion: {get_magenta_string(percent_completion)}{spacer}"
                     f"Duration: {get_magenta_string(duration_str)}{spacer}"
                     f"Completion ETA: {get_magenta_string(eta_str)}")
    sys.stdout.flush()
