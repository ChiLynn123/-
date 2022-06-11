import signal, time, re, base64, os
from io import BytesIO
from collections import namedtuple
from copy import deepcopy
import socket
from multiprocessing import Process, Queue
import asyncio
from html.parser import HTMLParser
from collections import defaultdict, deque
import uuid
from functools import partial, wraps
import cProfile, pstats, io
from pstats import SortKey

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import UnexpectedAlertPresentException
import psutil
from bs4 import BeautifulSoup
from PIL import ImageFont, ImageDraw, Image
from fake_useragent import Provider
import requests


def time_profile(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        pr = cProfile.Profile()
        pr.enable()
        result = func(*args, **kwargs)
        pr.disable()
        s = io.StringIO()
        sortby = SortKey.CUMULATIVE
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        ps.print_stats()
        print(s.getvalue())
        return result
    return wrapper
# set default socket timeout prevent selenium blocking.
# for testing
try:
    from settings import SLEEP_TIME, SOCKETTIMEOUT, WAIT_TIME
except Exception:
    SLEEP_TIME = 5
    SOCKETTIMEOUT = 1
    WAIT_TIME = 5
# setting socket timeout. Affect the selenium connects with webdriver.
socket.setdefaulttimeout(SOCKETTIMEOUT)
try:
    from logs_config.log_adapter import socket_Adapter as logger_rule

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


async def ping(url, wait=WAIT_TIME):
    live = False
    try:
        p = Provider(mobile=False)
        ua = p.chrome()
    except Exception as e:
        logger_rule.info(f"fake_ua failed.{e}")
        ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"
    headers = {"user-agent": ua}
    try:
        with requests.get(url, stream=True, timeout=wait, headers=headers):
            live = True
    except Exception as e:
        logger_rule.debug(e)
    logger_rule.info(f"url:{url} live:{live}")
    return live


async def check_scheme(domain):
    http_ping = asyncio.create_task(ping(f"http://{domain}"))
    https_ping = asyncio.create_task(ping(f"https://{domain}"))
    L = await asyncio.gather(
        asyncio.wait_for(http_ping, 5),
        asyncio.wait_for(https_ping, 5),
        return_exceptions=True,
    )
    return L


async def check_connect(url):
    url_ping = asyncio.create_task(ping(url))
    try:
        ret = await asyncio.wait_for(url_ping, 5)
    except asyncio.exceptions.TimeoutError as e:
        logger_rule.debugs(e)
        ret = False
    return ret


def ping2(url, wait=WAIT_TIME):
    live = False
    try:
        p = Provider(mobile=False)
        ua = p.chrome()
        # logger_rule.info(f"ua{ua}")
    except Exception as e:
        logger_rule.info(f"fake_ua failed.{e}")
        ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"
    headers = {"user-agent": ua}
    try:
        with requests.get(url, stream=True, timeout=wait, headers=headers):
            live = True
    except Exception as e:
        logger_rule.debug(e)

    return live


class MyHTMLParser(HTMLParser):
    def __init__(self,):
        super().__init__()
        self.tagCnt = defaultdict(int)
        self.textList = list()
        self.allTagCnt = 0

    def handle_starttag(self, tag, attrs):
        self.tagCnt[tag] += 1
        self.allTagCnt += 1

    def handle_startendtag(self, tag, attrs):
        self.tagCnt[tag] += 1
        self.allTagCnt += 1

    def handle_data(self, data):
        self.textList.append(data)

    @property
    def textCnt(self,):
        return len("".join(self.textList))


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
                return self.__phantomjs_init()

        def __chrome_init(self,):
            """return chrome driver"""
            try:
                p = Provider(mobile=False)
                ua = p.chrome()
            except Exception as e:
                logger_rule.info(f"fake_ua failed.{e}")
                ua = (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    + "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"
                )

            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument("--ignore-certificate-errors")
            chrome_options.add_argument("--ignore-ssl-errors=true")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("disable-web-security")
            chrome_options.add_argument("--disable-browser-side-navigation")
            chrome_options.add_argument("no-sandbox")
            chrome_options.add_argument("headless")
            chrome_options.add_argument("window-size=1920x2160")
            chrome_options.add_argument("--hide-scrollbars")
            chrome_options.add_argument("disable-dev-shm-usage")
            chrome_options.add_argument(f"user-agent={ua}")
            capa = deepcopy(DesiredCapabilities.CHROME)
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
                # service_args=["--verbose", "--log-path=./chrome_driver.log"],
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
                http_live = False
                try:
                    # todo can optimize with requests adaptor to retry.
                    http_live = ping2(f"http://{self.url}")
                except Exception as e:
                    logger_rule.info(f"http://{self.url} open failed.coursed by: {e}")
                if http_live:
                    url = f"http://{self.url}"
                else:
                    url = f"https://{self.url}"
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

    def __init__(self, url, time_wait=SLEEP_TIME, driver_type="chrome"):
        self.url = url
        self.driver_type = driver_type
        self.time_wait = time_wait

    def __enter__(self,):
        self.deal = Crawler._deal_crawl(self.url, self.driver_type)
        self.driver_pid_info = self.deal.driver_pid_info
        logger_rule.info(f"{self.url} crawl start.")
        logger_rule.debug(f"{self.url} crawl start at {self.driver_pid_info}")
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
                    logger_rule.error(
                        f"{self.url}self.deal.driver.current_url alert close failed."
                    )
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

            time.sleep(0.5)
            logger_rule.info(f"{self.url} use 0.5 sec to wait {c_pid} halt.")
        if psutil.pid_exists(c_pid):
            raise ValueError(f"chromedriver pid:{c_pid} terminates Failed.")
        for children_id in self.driver_pid_info.children_pid_list:
            if psutil.pid_exists(children_id):
                try:
                    p = psutil.Process(children_id)
                except Exception:
                    logger_rule.error("p = psutil.Process({children_id}) NoSuchProcess")

                else:
                    logger_rule.error(
                        f"chrome driver{c_pid} children_pid {children_id} exists."
                    )
                    try:
                        p.send_signal(signal.SIGTERM)
                    except psutil.NoSuchProcess:
                        pass
        logger_rule.debug(f"{self.deal.url} abnormal check finish.")

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


class CrawlerPlus(Crawler):
    def __init__(self, url, time_wait=SLEEP_TIME, screen=True, driver_type="chrome"):
        super().__init__(url, time_wait, driver_type)
        self.screen = screen

    def __getCurUrl(self):
        """get cur_url and will deal alert."""
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
                    logger_rule.error(
                        f"{self.url}self.deal.driver.current_url alert close failed."
                    )
                else:
                    logger_rule.info(f"{self.url} alert close success.")
        except Exception as e:
            logger_rule.error(
                f"{self.url} deal.driver.current_url Failed: coursed by {e}"
            )

    def __checkWebEmpty(self):
        """check page source is None or empty"""
        empty = True
        # get current url and check alert error.
        self.__getCurUrl()
        if self.deal.cur_url:
            self.deal._page_source()
            if self.deal.page_source != "<html><head></head><body></body></html>":
                empty = False
        return empty

    def __switchToRightIframe(self, iframeList):
        """loop the iframe tag of html content find the right iframe
            If:
                length of iframelist is 1, switch to it.
            else:
                If iframeItem has <title> tag  switch to it.
                if all iframe don't have <title>  can't find the right 
                iframe use default iframe.

            Args:
                iframeList: selenium web element item list.

            Returns:
                switch: True or False.

            Raises:
        """

        for iframeItem in iframeList:
            self.deal.driver.switch_to.default_content()
            try:
                self.deal.driver.switch_to.frame(iframeItem)
            except Exception as e:
                logger_rule.error(f"{self.url} switch to iframe failed, coursed by {e}")
            else:
                title_exists = self.deal.driver.find_elements_by_tag_name("title")
                if title_exists and title_exists[0].text != "":
                    return True
        # switch to main frame if not find right iframe.
        self.deal.driver.switch_to.default_content()
        return False

    def __checkWebVariety(self):
        """Using tag counts or length counts to check html is complete."""
        pass

    def __tagCount(self,):
        parser = MyHTMLParser()
        if self.deal.page_source:
            parser.feed(self.deal.page_source)
        else:
            parser.feed("<html><head></head><body></body></html>")
        return parser

    # @time_profile
    def __enter__(self):
        self.deal = Crawler._deal_crawl(self.url, self.driver_type)
        self.driver_pid_info = self.deal.driver_pid_info
        logger_rule.info(f"{self.url} crawl start.")
        logger_rule.debug(f"{self.url} crawl start at {self.driver_pid_info}")
        # crawler start.
        self.deal._get()
        # hard wait 5 secs.
        if self.time_wait < 0:
            time_wait = 5
        else:
            time_wait = self.time_wait
        # !total start with 5 doesn't mean it is five seconds.
        total = 5
        time.sleep(time_wait)

        # check crawler is empty if empty refresh.
        # the web site will wait extra 5 secs.
        if self.__checkWebEmpty():
            try:
                self.deal.driver.refresh()
            except Exception as e:
                logger_rule.error(f"{self.url} crawler refresh error coursed by{e}")
            else:
                logger_rule.info(f"{self.url} crawler refresh.")
            total += 5
            time.sleep(5)

        # check the  iframe tag

        iframelist = self.deal.driver.find_elements_by_tag_name("iframe")

        switchLoopTime = 3
        if iframelist:
            logger_rule.info(f"{self.url} contains {len(iframelist)} iframe tags.")
            switch = self.__switchToRightIframe(iframelist)
            while not switch and switchLoopTime > 0:
                switch = self.__switchToRightIframe(iframelist)
                switchLoopTime -= 1
                total += 1
                time.sleep(0.4)
            logger_rule.info(f"{self.url} switch to iframe {switch}")
        # check the item vary Variety.
        parserResult = self.__tagCount()
        logger_rule.info(f"parserResult.allTagCnt:{parserResult.allTagCnt}")
        preAllTagCnt = parserResult.allTagCnt
        logger_rule.info(f"parserResult.textCnt:{parserResult.textCnt}")
        preTextCnt = parserResult.textCnt
        d = deque([(preAllTagCnt, preTextCnt)], maxlen=2)
        while total < 20:
            # get current url and get pagesource
            self.__getCurUrl()
            self.deal._page_source()
            total += 1
            time.sleep(1)
            parserResult = self.__tagCount()
            preAllTagCnt, preTextCnt = d.pop()
            if (
                preTextCnt == parserResult.textCnt
                and preAllTagCnt == parserResult.allTagCnt
            ):
                if len(d) == 0:
                    d.append((preAllTagCnt, preTextCnt))
                    d.append((parserResult.allTagCnt, parserResult.textCnt))
                else:
                    logger_rule.info(f"the right total:{total}")
                    break
            else:
                d.clear()
                d.append((parserResult.allTagCnt, parserResult.textCnt))

        if self.deal.cur_url and self.screen:
            self.deal._screenshot_as_png()
        logger_rule.info(f"len(self.deal.page_source){len(self.deal.page_source)}")
        return self.deal


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
            20,
            102,
            font=font,
            text=self.watermark_text,
            shadowcolor=self.__shadowcolor,
            fillcolor=(255, 0, 0),
        )
        width, height = img.size
        # img = img.crop([0, 0, width, height / 2])
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


def chrome_spider(query, **kwargs):
    """
    if screen = False , chrome_spider while not take as sreenshot.
    if ping = True, chrome_spider will ping url first else will not ping.
    if set sleep_time, chrome_spider will wait setting time else wait 5 secs.
    return:rightResult or failedResult.
    """
    queryConnection = True
    url = None
    if query.startswith("http"):
        if kwargs.get('ping'):
            queryConnection = asyncio.run(check_connect(query))
        url = query
    else:
        httpConnection, httpsConnection = asyncio.run(check_scheme(query))
        if httpConnection ^ httpsConnection:
            url = f"http://{query}" if httpConnection else f"https://{query}"
        else:
            if httpConnection:
                url = f"http://{query}"
            else:
                queryConnection = False

    # take sleep time
    if kwargs.get('sleep_time'):
        sleep_time = kwargs.get('sleep_time')
    else:
        sleep_time = SLEEP_TIME

    if queryConnection:
        driverOpen = True
        try:
            if kwargs.get('screen') == False:
                args = (url, sleep_time, False)
            else:
                args = (url, sleep_time)
            with CrawlerPlus(*args) as crawler:
                html_origin_content = crawler.page_source
                scrrenshot_binary = crawler.scrrenshot_binary
                cur_url = crawler.cur_url
        except Exception as e:
            logger_rule.critical(
                f"{query} Crawler() failed, driver didn't start up. caursed by :{e}"
            )
            html_origin_content = None
            driverOpen = False
        finally:
            # logger_rule.info(f"html_origin_content:{html_origin_content}")
            if (
                html_origin_content is None
                or html_origin_content == "<html><head></head><body></body></html>"
            ):  # crawler failed.
                if not driverOpen:
                    result = failedResult._make(
                        [False, query, "critical driver open failed."]
                    )
                else:
                    logger_rule.info(
                        f"{query} crawl failed coursed by no html content."
                    )
                    result = failedResult._make([False, query, "crawl failed."])
            else:
                he = htmlExtract(html_origin_content)
                html_content, title_content = he.html_content, he.title_content
                if scrrenshot_binary:
                    wm = Watermark(scrrenshot_binary, [query, title_content])
                    screen_base64 = wm.wm_png_base64
                else:
                    screen_base64 = None
                result = rightResult._make(
                    [
                        True,
                        query,
                        html_content,
                        title_content,
                        html_origin_content,
                        cur_url,
                        screen_base64,
                    ]
                )
    else:
        logger_rule.info(f"{query} crawl failed coursed by ping time out.")
        result = failedResult._make([False, query, "ping time out."])
    return result


def spider_write(query):
    spider_result = chrome_spider(query)


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

    def filename_check(filename, path, suffix=""):
        """

        To check filename when write content to file. If path has
        same filename will add  _{cnt} to the suffix of filename.

        filename: write filename
        path: the directory of file
        suffix: the suffix of file eg '.txt', '.png' 
        """
        filenameExists = True
        cnt = 0
        origin = filename
        while filenameExists:
            filePath = os.path.join(path, f"{filename}{suffix}")
            if os.path.exists(filePath):
                filename = f"{origin}_{cnt}"
                cnt += 1
            else:
                filenameExists = False

        return filename

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
        "-logname", "-l", type=str, dest="user_log", help="user define log filename.",
    )
    parser.add_argument(
        "-level",
        choices=["DEBUG", "INFO", "WARNNING", "CRITICAL"],
        dest="loglevel",
        help="user define log level. default INFO.",
    )
    parser.add_argument(
        "-scheme",
        "-sch",
        choices=["http", "https"],
        dest="scheme",
        help="""If user didn't set domain's scheme , program will ping http first.
        If http scheme connect program will crawl http://{domain},
         otherwise it will crawl https://{domain}.""",
    )
    args = parser.parse_args()
    urlfilename = os.path.basename(args.infile.name)
    task_dir = f"{urlfilename.split('.')[0]}_{time.strftime('%Y%m%d_%H%M%S')}"
    result_dir = os.path.join("crawler_result", task_dir)
    if not os.path.exists(result_dir):
        os.mkdir(result_dir)
    urllist = []
    if args.scheme:
        if args.scheme == "http":
            for line in args.infile.readlines():
                line = line.strip()
                if not line.startswith("http"):
                    line = f"http://{line}"
                else:
                    # already startswith http:
                    pass
                urllist.append(line)
        elif args.scheme == "https":
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

    if args.process:
        process = args.process
    else:
        process = 2

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

    def multi_test(urllist, result_dir, process=2, sleep_time=SLEEP_TIME):
        start_time = time.time()
        start_time_str = time.strftime("%Y-%m-%d %H:%M:%S")
        if process > 1:
            with Pool(process) as p:
                from functools import partial
                chrome_spider_p = partial(chrome_spider, sleep_time=sleep_time, ping=True)
                results = p.map(chrome_spider_p, urllist)
        elif process == 1:
            results = [chrome_spider(url, sleep_time=sleep_time, ping=True) for url in urllist]

        scheme = args.scheme if args.scheme else "default"

        statics = {
            "start_time": start_time_str,
            "finish_time": None,
            "time_consume": None,
            "success": 0,
            "failed": 0,
            "screened": 0,
            "time_wait": SLEEP_TIME,
            "scheme": scheme,
        }
        parameter = f"w_{SLEEP_TIME}_s_{scheme}"
        with open(
            os.path.join(result_dir, f"result_{parameter}.csv"),
            "w",
            newline="",
            encoding="utf-8",
        ) as csvfile:
            fieldnames = [
                "judge",
                "url",
                "cur_url",
                "title",
                "html_content",
                "html_id",
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            pics_dir = os.path.join(result_dir, "pics")
            htmls_dir = os.path.join(result_dir, "htmls")
            if not os.path.exists(pics_dir):
                os.mkdir(pics_dir)
            if not os.path.exists(htmls_dir):
                os.mkdir(htmls_dir)

            for item in results:
                tmp_dict = {}
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
                writer.writerow(tmp_dict)
                if item.judge:
                    if item.screen_base64:
                        with open(
                            os.path.join(pics_dir, f"{u_id}.png"), "wb"
                        ) as outfile:
                            try:
                                outfile.write(base64.b64decode(item.screen_base64))
                                statics["screened"] += 1
                            except Exception as e:
                                logger_rule.error(
                                    f"outfile.write(base64.b64decode(item.screen_base64)){e}"
                                )
                    if item.html_origin_content:
                        with open(
                            os.path.join(htmls_dir, f"{u_id}.html"), "w"
                        ) as outfile:
                            try:
                                outfile.write(item.html_origin_content)
                            except Exception as e:
                                logger_rule.error(
                                    f"outfile.write(item.html_origin_content){e}"
                                )

            statics["time_consume"] = f"{round(time.time() - start_time,2)} secs."
            statics["finish_time"] = time.strftime("%Y-%m-%d %H:%M:%S")
            logger_rule.info(f"crawler statics info {statics}")

    multi_test(urllist, result_dir, process)
