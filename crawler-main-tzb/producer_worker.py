# multiprocessing_producer_consumer.py
# https://pymotw.com/3/multiprocessing/communication.html

import multiprocessing
import time
import csv
import json
import sys
import pathlib
import uuid
import os
import logging
import base64
import argparse

from crawler import chrome_spider

csv.field_size_limit(500 * 1024 * 1024)
# todo statics
statics = {}
statics["success"] = 0
statics["screened"] = 0
statics["failed"] = 0

logger_rule = logging


class Consumer(multiprocessing.Process):
    def __init__(self, task_queue, result_dir):
        multiprocessing.Process.__init__(self)
        self.task_queue = task_queue
        self.result_dir = pathlib.Path(result_dir)

    def run(self):
        proc_name = self.name
        fieldnames = [
            "judge",
            "url",
            "cur_url",
            "title",
            "html_content",
            "html_id",
        ]
        pics_dir = self.result_dir / "pics"
        htmls_dir = self.result_dir / "htmls"

        with open(
            self.result_dir / f"{proc_name}.csv", "w", encoding="utf-8"
        ) as csvfile:
            csv_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            while True:
                query = self.task_queue.get()
                if query is None:
                    # Poison pill means shutdown
                    print("{}: Exiting".format(proc_name))
                    self.task_queue.task_done()
                    break
                item = chrome_spider(query)
                u_id = uuid.uuid1()
                if item.judge:
                    #
                    tmp_dict = {
                        "judge": item.judge,
                        "url": item.url,
                        "cur_url": item.cur_url,
                        "title": item.title_content,
                        "html_content": item.html_content.replace("\r\n", "").replace(
                            "\n", ""
                        ),
                        "html_id": u_id,
                    }
                    statics["success"] += 1
                    if item.screen_base64:
                        with open(pics_dir / f"{u_id}.png", "wb") as outfile:
                            try:
                                outfile.write(base64.b64decode(item.screen_base64))
                                statics["screened"] += 1
                            except Exception as e:
                                logger_rule.error(
                                    f"outfile.write(base64.b64decode(item.screen_base64)){e}"
                                )
                    if item.html_origin_content:
                        with open(htmls_dir / f"{u_id}.html", "w") as outfile:
                            try:
                                outfile.write(item.html_origin_content)
                            except Exception as e:
                                logger_rule.error(
                                    f"outfile.write(item.html_origin_content){e}"
                                )
                else:
                    tmp_dict = {
                        "judge": item.judge,
                        "url": item.url,
                        "cur_url": None,
                        "title": None,
                        "html_content": None,
                        "html_id": u_id,
                    }
                    statics["failed"] += 1
                csv_writer.writerow(tmp_dict)
                csvfile.flush()

                self.task_queue.task_done()


if __name__ == "__main__":
    # Establish communication queues
    tasks = multiprocessing.JoinableQueue()
    results = multiprocessing.Queue()
    seed_path = pathlib.Path("crawler_seed")
    result_base_path = pathlib.Path("crawler_result")
    if not seed_path.exists:
        os.mkdir("crawler_result")
    if not result_base_path.exists():
        os.mkdir("crawler_seed")
    # Start consumers
    # todo num_consumer use args.process
    parser = argparse.ArgumentParser(description="Crawler producer and consumer function.")
    parser.add_argument(
        "-seed",
        "-s",
        type=argparse.FileType("r", encoding="utf-8"),
        dest="infile",
        help="input url txt.",
        required=True,
    )
    parser.add_argument(
        "-process",
        "-p",
        type=int,
        dest="process",
        help="number of process in crawler. default 2.",
    )
    parser.add_argument(
        "-wait",
        "-w",
        type=int,
        dest="time_wait",
        help="each crawler wait secs. default 30. ",
    )
    parser.add_argument(
        "-num",
        "-n",
        type=int,
        dest="num",
        help="deal numbers lines in url txt. default -1.",
    )
    args = parser.parse_args()

    num_consumers = args.process

    print("Creating {} consumers".format(num_consumers))
    parser = argparse.ArgumentParser(description="Crawler test function")
    urlfilename = os.path.basename(args.infile.name)
    task_dir = f"{urlfilename.split('.')[0]}_{time.strftime('%Y%m%d_%H%M%S')}"
    result_dir = result_base_path / task_dir
    if not result_dir.exists():
        os.mkdir(result_dir)
    consumers = [Consumer(tasks, result_dir) for i in range(num_consumers)]
    # todo urllist
    urllist = [line.strip() for line in args.infile.readlines()]
    for w in consumers:
        w.start()

    # Enqueue jobs
    i = 0
    if args.num and args.num > 0:
        nums = args.num
    else:
        nums = -1
    for row in urllist[:nums]:
        tasks.put(row)
        i += 1
    print(f"all deal {i}")

    # Add a poison pill for each consumer
    for i in range(num_consumers):
        tasks.put(None)

    # Wait for all of the tasks to finish

    def merge_result(result_dir):
        tasks.join()
        all_csv = []
        for file in result_dir.iterdir():
            # print(file.suffix)
            if file.suffix == '.csv':
                with open(file, "r", encoding="utf-8", newline="") as infile:
                    all_csv.append(infile.read())
                os.remove(file)

        parameter = "all"
        with open(
            result_dir / f"result_{parameter}.csv", "w", encoding="utf-8"
        ) as outfile:

            for csv_content in all_csv:
                outfile.write(csv_content)
    pics_dir = result_dir / "pics"
    htmls_dir = result_dir / "htmls"
    if not pics_dir.exists():
        os.mkdir(pics_dir)
    if not htmls_dir.exists():
        os.mkdir(htmls_dir)
    merge_result(result_dir)
