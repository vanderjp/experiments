import asyncio
import multiprocessing
import os
from concurrent.futures.thread import ThreadPoolExecutor
from multiprocessing import Lock
from multiprocessing import Value
from time import time
from typing import Optional

from loguru import logger

import logging_utilities

# start_time: Optional[float] = None


async def do_a_slow_thing(thing_number):
    global slow_thing_duration
    global total_jobs

    logging_utilities.print_eta(thing_number, start_time, total_jobs)

    logger.debug(f"\tstarting thing {thing_number} on process {os.getpid()}...")
    await asyncio.sleep(slow_thing_duration)
    logger.info(f"\tfinished thing {thing_number} on process {os.getpid()}...")


# def do_slow_things_serially(count: int):
#     logger.info("********** SERIAL RESULTS **********")
#     while count > 0:
#         do_a_slow_thing(count)
#         count -= 1


def execute_slow_thing_based_on_counter():
    global lock
    global counter
    global total_jobs

    while True:
        thing_number: int = -1
        is_do_slow_thing: bool = False
        with lock:
            if counter.value <= total_jobs:
                thing_number = counter.value
                counter.value += 1
                is_do_slow_thing = True

        if is_do_slow_thing:
            asyncio.run(do_a_slow_thing(thing_number))
        else:
            break


def do_slow_things_multithread():
    global lock
    global counter
    global threadCount

    logging_utilities.configure_logger(is_delete_existing=False)
    logger.info("********** THREADED RESULTS **********")

    with ThreadPoolExecutor(max_workers=threadCount) as pool:
        for _ in range(threadCount):
            pool.submit(execute_slow_thing_based_on_counter)


def processInit(aCounter, aLock, aThreadCount, a_slow_thing_duration, a_total_jobs, a_start_time):
    global lock
    global counter
    global threadCount
    global slow_thing_duration
    global total_jobs
    global start_time

    lock = aLock
    counter = aCounter
    threadCount = aThreadCount
    slow_thing_duration = a_slow_thing_duration
    total_jobs = a_total_jobs
    start_time = a_start_time


def do_slow_things_multiprocess_multithread():
    global lock
    global counter
    global threadCount
    global processCount
    global slow_thing_duration
    global total_jobs
    global start_time

    logger.info("********** MULTIPROCESS RESULTS **********")

    with multiprocessing.Pool(initializer=processInit,
                              initargs=(counter, lock, threadCount, slow_thing_duration, total_jobs,
                                        start_time)) as pool:
        for _ in range(processCount):
            pool.apply_async(do_slow_things_multithread)
        pool.close()
        pool.join()

    logger.success(f"processing took {time() - start_time} to complete")


if __name__ == '__main__':
    logging_utilities.configure_logger()

    counter: Value = Value("i", 1)
    lock: Lock() = Lock()
    slow_thing_duration: int = 3
    total_jobs: int = 500
    threadCount: int = 10
    processCount: int = multiprocessing.cpu_count() - 1

    start_time = time()

    # do_slow_things_serially(counter.value)
    # do_slow_things_multithread()
    do_slow_things_multiprocess_multithread()

    print(logging_utilities.get_final_summary(start_time, total_jobs))
