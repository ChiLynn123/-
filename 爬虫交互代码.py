import os, signal, time
from io import BytesIO
from collections import namedtuple
import re, base64
from collections import namedtuple


from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import UnexpectedAlertPresentException
import psutil
from bs4 import BeautifulSoup
from PIL import ImageFont, ImageDraw, Image


# todo for testing
try:
    from settings import SLEEP_TIME

    raise
except Exception:
    SLEEP_TIME = 30

try:
    from core.con_log import logger_rule

    raise
except Exception:
    import logging

    logger_rule = logging.getLogger()
    # default logger level is debug
    logger_rule.setLevel(logging.DEBUG)
    format_type = "%(asctime)s  %(filename)s %(funcName)s: %(levelname)s  %(message)s"
    formatter = logging.Formatter(format_type, datefmt="%Y-%m-%d %A %H:%M:%S")
    if not os.path.exists("Logs"):
        os.mkdir("Logs")
    # default log set overwirte mode.
    default_handler = logging.FileHandler("Logs/Crawler.log", mode="w")
    default_handler.setLevel(logging.DEBUG)
    default_handler.setFormatter(formatter)
    logger_rule.addHandler(default_handler)

    stream = logging.StreamHandler()
    stream.setLevel(logging.INFO)
    stream.setFormatter(formatter)
    logger_rule.addHandler(stream)

rightResult = namedtuple(
    "rightResult",
    [
        "judge",
        "url",
        "html_content",
        "title_content",
        "html_origin_content",
        "cur_url",
        "screen_base64",
    ],
)
failedResult = namedtuple("failedResult", ["judge", "url", "errorValue"])


class Crawler(object):
    class _deal_crawl(object):
        def __init__(self, url, driver_type="chrome"):
            self.driver_type = driver_type
            self.url = url
            self.driver = self.__init_driver()
            self.driver_pid_info = self.__get_driver_pid_info()
            self.cur_url = None
            self.page_source = None
            self.scrrenshot_binary = None

        def _close(self,):
            self.driver.delete_all_cookies()
            self.driver.quit()

        def __init_driver(self,):
            if self.driver_type == "chrome":
                return self.__chrome_init()
            if self.driver_type == "firefox":
                return self.__firefox_init()
            if self.driver_type == "phantomjs":
                return self.__phantomjs()

        def __chrome_init(self,):
            """return chrome driver"""
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument("--ignore-certificate-errors")
            chrome_options.add_argument("--ignore-ssl-errors=true")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("disable-web-security")
            chrome_options.add_argument("--disable-browser-side-navigation")
            chrome_options.add_argument("no-sandbox")
            chrome_options.add_argument("headless")
            chrome_options.add_argument("window-size=1920x3000")
            chrome_options.add_argument("--hide-scrollbars")
            chrome_options.add_argument("disable-dev-shm-usage")

            capa = DesiredCapabilities.CHROME
            capa["pageLoadStrategy"] = "none"
            prefs = {
                "download.prompt_for_download": True,
                "download.default_directory": "/dev/null",
            }
            chrome_options.add_experimental_option("prefs", prefs)
            return webdriver.Chrome(
                executable_path="/usr/bin/chromedriver",
                options=chrome_options,
                desired_capabilities=capa,
            )

        def __firefox_init(self,):
            """return firefox driver"""
            pass

        def __phantomjs_init(self,):
            """return phantomjs driver"""
            pass

        def __get_driver_pid_info(self,):
            if self.driver_type is None or self.driver is None:
                raise ValueError("Should init a webdriver")
            _pid_info = namedtuple(
                "pid_info", ["chrome_driver_pid", "children_pid_list"]
            )
            if self.driver_type == "chrome":
                chrome_driver_pid = self.driver.service.process.pid
                p = psutil.Process(chrome_driver_pid)
                children_pid_list = []
                for driver_children in p.children(recursive=True):
                    children_pid_list.append(driver_children.pid)
                driver_pid_info = _pid_info._make(
                    [chrome_driver_pid, children_pid_list]
                )
            return driver_pid_info

        def _get(self,):

            if not self.url.startswith("http"):
                url = f"http://{self.url}"
            else:
                url = self.url
            try:
                self.driver.get(url)
                logger_rule.debug(f"{url}self.driver.get")
            except Exception as e:
                logger_rule.error(f"{url} driver.get Failed: coursed by {e}")

        def _page_source(self,):
            try:
                self.page_source = self.driver.page_source
                logger_rule.debug(f"{self.url} driver.page_source {self.page_source}")
            except Exception as e:
                logger_rule.error(
                    f"{self.url} driver.page_source Failed: coursed by {e}"
                )

        def _screenshot_as_png(self,):
            """return  images binary string"""
            try:
                png_bytes = self.driver.get_screenshot_as_png()
                logger_rule.debug(f"{self.url}self.driver.get_screenshot_as_png")
            except Exception as e:
                logger_rule.error(
                    f"{self.url} driver.get_screenshot_as_png Failed: coursed by {e}"
                )
            else:
                self.scrrenshot_binary = png_bytes

    def __init__(self, url, time_wait=20, driver_type="chrome"):
        self.url = url
        self.driver_type = driver_type
        self.time_wait = time_wait

    def __enter__(self,):
        self.deal = Crawler._deal_crawl(self.url, self.driver_type)
        self.driver_pid_info = self.deal.driver_pid_info
        logger_rule.info(f"{self.url} crawl start at {self.driver_pid_info}")
        self.deal._get()
        time.sleep(self.time_wait)
        try:
            self.deal.cur_url = self.deal.driver.current_url
        except UnexpectedAlertPresentException as e:
            try:
                WebDriverWait(self.deal.driver, 3).until(EC.alert_is_present())
                self.deal.driver.switch_to.alert.dismiss()
            except TimeoutException:
                try:
                    self.deal.cur_url = self.deal.driver.current_url
                except UnexpectedAlertPresentException as e:
                    self.error(
                        f"{self.url}self.deal.driver.current_url alert close failed."
                    )
                    self.deal.cur_url = None
                else:
                    logger_rule.info(f"{self.url} alert close success.")
        except Exception as e:
            logger_rule.error(
                f"{self.url} deal.driver.current_url Failed: coursed by {e}"
            )
        # only self.deal.cur_url exists get screenshot
        if self.deal.cur_url:
            self.deal._page_source()
            self.deal._screenshot_as_png()
        return self.deal

    def __close_abnormal_chrome(self,):
        c_pid = self.driver_pid_info.chrome_driver_pid
        if psutil.pid_exists(c_pid):
            logger_rule.error(f"{self.url} chrome driver {c_pid} exists.")
            Crawler.kill_proc_tree(c_pid)
            # 留给程序关闭的预留时间

            time.sleep(0.5)
            logger_rule.info(f"{self.url} use 0.5 sec to wait {c_pid} halt.")
        if psutil.pid_exists(c_pid):
            raise ValueError(f"chromedriver pid:{c_pid} terminates Failed.")
        for children_id in self.driver_pid_info.children_pid_list:
            if psutil.pid_exists(children_id):
                try:
                    p = psutil.Process(children_id)
                except Exception as e:
                    logger_rule.error("p = psutil.Process({children_id}) NoSuchProcess")

                else:
                    logger_rule.error(
                        f"chrome driver{c_pid} children_pid {children_id} exists."
                    )
                    try:
                        p.send_signal(signal.SIGTERM)
                    except psutil.NoSuchProcess:
                        pass
        logger_rule.info(f"{self.deal.url} abnormal check finish.")

    @staticmethod
    def kill_proc_tree(
        pid, sig=signal.SIGTERM, include_parent=True, timeout=None, on_terminate=None
    ):
        assert pid != os.getpid(), "don't kill myself"
        parent = psutil.Process(pid)
        children = parent.children(recursive=True)
        if include_parent:
            children.append(parent)
        for p in children:
            try:
                p.send_signal(sig)
            except psutil.NoSuchProcess:
                pass
        gone, alive = psutil.wait_procs(
            children, timeout=timeout, callback=on_terminate
        )
        return (gone, alive)

    def __exit__(self, type, value, traceback):
        try:
            self.deal._close()
        except Exception as e:
            logger_rule.error(f"{self.url} self.deal._close failed: course by {e}")
        self.__close_abnormal_chrome()
        logger_rule.info(f"{self.deal.url} crawl finish!")


class htmlExtract(object):
    def __init__(
        self, page_source,
    ):
        self.page_source = page_source
        self.title_content, self.html_content = self.__get_data()

    def __get_data(self,):
        soup = BeautifulSoup(self.page_source.strip(), "lxml")
        try:
            title_content = soup.title.string.strip()
        except (AttributeError, KeyError):
            title_content = ""
        for tag in soup(["style", "script"]):
            tag.decompose()
        clean_data = re.sub(
            r"[^\u4e00-\u9fa50-9a-zA-z\s]+", "", soup.get_text().strip()
        )
        html_content = re.sub(r"[\s]+", r" ", clean_data)
        return title_content, html_content


class Watermark(object):
    def __init__(
        self,
        png_binary,
        text_list,
        width_resize=2,
        height_resize=2,
        shadowcolor="black",
        font_size=36,
        sep="\n",
        font="wqy-zenhei.ttc",
    ):
        self.png_binary = png_binary
        self.watermark_text = sep.join(text_list)
        self.__font_size = font_size
        self.__shadowcolor = shadowcolor
        self.__font = font
        self.__width_resize = width_resize
        self.__height_resize = height_resize
        self.wm_png_binary = self.__watermark()

    def __text_border(self, draw, x, y, font, text, shadowcolor, fillcolor):
        # thin border
        draw.text((x - 1, y), text, font=font, fill=shadowcolor)
        draw.text((x + 1, y), text, font=font, fill=shadowcolor)
        draw.text((x, y - 1), text, font=font, fill=shadowcolor)
        draw.text((x, y + 1), text, font=font, fill=shadowcolor)

        # thicker border
        draw.text((x - 1, y - 1), text, font=font, fill=shadowcolor)
        draw.text((x + 1, y - 1), text, font=font, fill=shadowcolor)
        draw.text((x - 1, y + 1), text, font=font, fill=shadowcolor)
        draw.text((x + 1, y + 1), text, font=font, fill=shadowcolor)

        # now draw the text over it
        draw.text((x, y), text, font=font, fill=fillcolor)

    def __watermark(self,):
        img = Image.open(BytesIO(self.png_binary))
        font = ImageFont.truetype(self.__font, self.__font_size)
        self.__text_border(
            ImageDraw.Draw(img),
            0,
            0,
            font=font,
            text=self.watermark_text,
            shadowcolor=self.__shadowcolor,
            fillcolor=(255, 0, 0),
        )
        width, height = img.size
        img = img.crop([0, 0, width / 1, height / 2])
        img = img.resize(
            (int(width / self.__width_resize), int(height / self.__height_resize)),
            Image.ANTIALIAS,
        )
        bytes_buffer = BytesIO()
        img.save(bytes_buffer, format="PNG")
        img.close()
        return bytes_buffer.getvalue()

    @property
    def wm_png_base64(self,):
        return base64.b64encode(self.wm_png_binary).decode()


def chrome_spider(url):

    with Crawler(url, SLEEP_TIME) as crawler:
        html_origin_content = crawler.page_source
        # none 爬取默认未爬取页面的返回结果
        if (
            html_origin_content is None
            or html_origin_content == "<html><head></head><body></body></html>"
        ):  # crawler failed.
            result = failedResult._make([False, url, "crawler failed."])
        else:
            he = htmlExtract(html_origin_content)
            html_content, title_content = he.html_content, he.title_content
            cur_url = crawler.cur_url
            if crawler.scrrenshot_binary:
                wm = Watermark(crawler.scrrenshot_binary, [url, title_content])
                screen_base64 = wm.wm_png_base64
            else:
                screen_base64 = None
            result = rightResult._make(
                [
                    True,
                    url,
                    html_content,
                    title_content,
                    html_origin_content,
                    cur_url,
                    screen_base64,
                ]
            )
    return result


if __name__ == "__main__":
    from multiprocessing import Pool
    import uuid
    import csv
    import sys
    import argparse
    import time

    if not os.path.exists("crawler_result"):
        os.mkdir("crawler_result")
    if not os.path.exists("crawler_seed"):
        os.mkdir("crawler_seed")

    parser = argparse.ArgumentParser(description="Crawler test function")
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
    parser.add_argument(
        "-log",
        "-l",
        type=str,
        dest="user_log",
        help="user define log filename. default INFO",
    )
    parser.add_argument(
        "-level",
        choices=["DEBUG", "INFO", "WARNNING", "CRITICAL"],
        dest="loglevel",
        help="user define log level.",
    )
    parser.add_argument(
        "-schema",
        "-sch",
        choices=["http", "https"],
        dest="schema",
        help="If url not have schema use http or https to be schema.",
    )
    args = parser.parse_args()
    urlfilename = os.path.basename(args.infile.name)
    task_dir = f"{urlfilename.split('.')[0]}_{time.strftime('%Y%m%d_%H%M%S')}"
    result_dir = os.path.join("crawler_result", task_dir)
    if not os.path.exists(result_dir):
        os.mkdir(result_dir)
    urllist = []
    if args.schema:
        if args.schema == "http":
            for line in args.infile.readlines():
                line = line.strip()
                if not line.startswith("http"):
                    line = f"http://{line}"
                else:
                    # already startswith http:
                    pass
                urllist.append(line)
        elif args.schema == "https":
            for line in args.infile.readlines():
                line = line.strip()
                if not line.startswith("http"):
                    line = f"https://{line}"
                else:
                    # already startswith https:
                    pass
                urllist.append(line)
    else:
        urllist = [line.strip() for line in args.infile.readlines()]

    if args.num:
        urllist = urllist[: args.num]
    else:
        urllist = urllist[:-1]

    if args.time_wait:
        SLEEP_TIME = args.time_wait

    process = 2
    if args.process:
        process = args.process

    if args.user_log:
        user_handler = logging.FileHandler(
            os.path.join(result_dir, f"{args.user_log}.log")
        )
        if args.loglevel:
            if args.loglevel == "DEBUG":
                user_handler.setLevel(logging.DEBUG)
            elif args.loglevel == "INFO":
                user_handler.setLevel(logging.INFO)
            elif args.loglevel == "WARNNING":
                user_handler.setLevel(logging.WARNING)
            else:
                user_handler.setLevel(logging.CRITICAL)
        else:
            # default INFO level log.
            user_handler.setLevel(logging.INFO)
        user_handler.setFormatter(formatter)
        logger_rule.addHandler(user_handler)
    else:
        pass

    def multi_test(urllist, result_dir, process=2):
        start_time = time.time()
        start_time_str = time.strftime("%Y-%m-%d %H:%M:%S")
        with Pool(process) as p:
            results = p.map(chrome_spider, urllist)

        schema = args.schema if args.schema else "default"

        statics = {
            "start_time": start_time_str,
            "finish_time": None,
            "time_consume": None,
            "success": 0,
            "failed": 0,
            "screened": 0,
            "time_wait": SLEEP_TIME,
            "schema": schema,
        }
        parameter = f"w_{SLEEP_TIME}_s_{schema}"
        with open(
            os.path.join(result_dir, f"result_{parameter}.csv"),
            "w",
            newline="",
            encoding="utf-8",
        ) as csvfile:
            fieldnames = ["judge", "url", "cur_url", "title", "html_content"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            pics_dir = os.path.join(result_dir, "pics")
            if not os.path.exists(pics_dir):
                os.mkdir(pics_dir)

            for item in results:
                tmp_dict = {}
                if item.judge:
                    tmp_dict = {
                        "judge": item.judge,
                        "url": item.url,
                        "cur_url": item.cur_url,
                        "title": item.title_content,
                        "html_content": item.html_content.replace("\r\n", "").replace(
                            "\n", ""
                        ),
                    }
                    statics["success"] += 1
                else:
                    tmp_dict = {
                        "judge": item.judge,
                        "url": item.url,
                        "cur_url": None,
                        "title": None,
                        "html_content": None,
                    }
                    statics["failed"] += 1
                writer.writerow(tmp_dict)
                html_idx = item.url.split("/")[-1]
                if item.judge and item.screen_base64:
                    with open(
                        os.path.join(pics_dir, f"{html_idx}.png"), "wb"
                    ) as outfile:
                        try:
                            outfile.write(base64.b64decode(item.screen_base64))
                            statics["screened"] += 1
                        except Exception as e:
                            logger_rule.error(
                                f"outfile.write(base64.b64decode(item.screen_base64)){e}"
                            )
            statics["time_consume"] = f"{round(time.time() - start_time,2)} secs."
            statics["finish_time"] = time.strftime("%Y-%m-%d %H:%M:%S")
            logger_rule.info(f"crawler statics info {statics}")

    multi_test(urllist, result_dir, process)