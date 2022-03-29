import asyncio
import multiprocessing
import os
from concurrent.futures.thread import ThreadPoolExecutor
from multiprocessing import Lock
from multiprocessing import Value
from time import time
from typing import Optional

import colorama
from loguru import logger

import logging_utilities

JOB_COUNTER: Optional[Value] = None
JOB_COUNTER_LOCK: Optional[Lock] = None
PROCESS_COUNT: Optional[int] = None
SLOW_THING_DURATION: Optional[int] = None
START_TIME: Optional[float] = None
THREAD_COUNT: Optional[int] = None
TOTAL_JOBS: Optional[int] = None


async def do_a_slow_thing(thing_number):

    logging_utilities.print_eta(thing_number, START_TIME, TOTAL_JOBS)

    logger.debug(f"\tstarting thing {thing_number} on process {os.getpid()}...")
    await asyncio.sleep(SLOW_THING_DURATION)
    logger.info(f"\tfinished thing {thing_number} on process {os.getpid()}...")


# def do_slow_things_serially(count: int):
#     logger.info("********** SERIAL RESULTS **********")
#     while count > 0:
#         do_a_slow_thing(count)
#         count -= 1


def execute_slow_thing_based_on_counter():
    while True:
        thing_number: int = -1
        is_do_slow_thing: bool = False
        with JOB_COUNTER_LOCK:
            if JOB_COUNTER.value <= TOTAL_JOBS:
                thing_number = JOB_COUNTER.value
                JOB_COUNTER.value += 1
                is_do_slow_thing = True

        if is_do_slow_thing:
            asyncio.run(do_a_slow_thing(thing_number))
        else:
            break


def do_slow_things_multithread():
    logging_utilities.configure_logger(is_delete_existing=False)
    logger.info("********** THREADED RESULTS **********")

    with ThreadPoolExecutor(max_workers=THREAD_COUNT) as pool:
        for _ in range(THREAD_COUNT):
            pool.submit(execute_slow_thing_based_on_counter)


def processInit(a_counter,
                a_counter_lock,
                a_slow_thing_duration,
                a_start_time,
                a_thread_count,
                a_total_jobs):
    global JOB_COUNTER
    global JOB_COUNTER_LOCK
    global SLOW_THING_DURATION
    global START_TIME
    global THREAD_COUNT
    global TOTAL_JOBS

    JOB_COUNTER = a_counter
    JOB_COUNTER_LOCK = a_counter_lock
    THREAD_COUNT = a_thread_count
    SLOW_THING_DURATION = a_slow_thing_duration
    TOTAL_JOBS = a_total_jobs
    START_TIME = a_start_time


def do_slow_things_multiprocess_multithread():
    global JOB_COUNTER_LOCK
    global JOB_COUNTER
    global THREAD_COUNT
    global PROCESS_COUNT
    global TOTAL_JOBS

    logger.info("********** MULTIPROCESS RESULTS **********")

    with multiprocessing.Pool(initializer=processInit,
                              initargs=(JOB_COUNTER,
                                        JOB_COUNTER_LOCK,
                                        SLOW_THING_DURATION,
                                        START_TIME,
                                        THREAD_COUNT,
                                        TOTAL_JOBS)) as pool:
        for _ in range(PROCESS_COUNT):
            pool.apply_async(do_slow_things_multithread)
        pool.close()
        pool.join()


if __name__ == '__main__':
    JOB_COUNTER = Value("i", 1)
    JOB_COUNTER_LOCK = Lock()
    PROCESS_COUNT = multiprocessing.cpu_count() - 1
    SLOW_THING_DURATION = 3
    START_TIME = time()
    THREAD_COUNT = 10
    TOTAL_JOBS = 500

    logging_utilities.configure_logger()

    colorama.init()

    # do_slow_things_serially(JOB_COUNTER.value)
    # do_slow_things_multithread()
    do_slow_things_multiprocess_multithread()

    print(f"\n\n{logging_utilities.get_final_summary(START_TIME, TOTAL_JOBS)}")
