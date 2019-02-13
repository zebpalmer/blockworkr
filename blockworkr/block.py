import logging
from threading import Lock, Thread
from datetime import datetime, timedelta
from time import sleep
import requests
from itertools import chain

# for initial api testing
from random import randint


class NotReady(Exception):
    pass


class Block:
    def __init__(self, blocklists=None, whitelists=None, disk_cache=False, frequency=30, cron=True):
        self.whitelists = whitelists
        self.blocklists = blocklists
        self.dist_cache = disk_cache
        self.frequency = frequency
        self.data = {}
        self._update_lock = Lock()
        self._update_thread = None
        self._update_thread_lock = Lock()
        self._ts_updated = None
        self._ts_next_update = datetime.utcnow()
        if cron:
            sched = Thread(target=self._cron, daemon=True)
            sched.start()

    def ready(self):
        if not self._ts_updated:
            return False
        else:
            return bool(self._ts_updated > datetime.utcnow() - timedelta(minutes=self.frequency * 2))

    def update(self, background=True):
        start = datetime.utcnow()
        if self._update_lock.locked() or self._update_thread_lock.locked():
            logging.debug("update already in progress")
            return False
        else:
            with self._update_lock:
                if self._ts_updated and self._ts_updated > start:
                    logging.debug("Update completed in another thread")
                    return True
                else:
                    if not background:
                        self._update_blockdata()
                    else:
                        self._update_thread = Thread(target=self._update_blockdata)
                        self._update_thread.start()

    def _cron(self):
        """
        just a stupid simple loop to ensure check_update gets called
        periodically
        """
        while True:
            self.check_update()
            sleep(60)

    def check_update(self):
        if self._ts_next_update < datetime.utcnow():
            self.update()

    def _update_blockdata(self):
        """
        This method updates the data
        Don't call this method directly, use update() or check_update()

        :return: runs an update cycle
        :rtype: dict
        """
        raw = {}
        logging.debug("blockdata is updating")
        start = datetime.utcnow()
        with self._update_thread_lock:
            raw["whitelists"] = {}
            raw["blocklists"] = {}
            for url in self.whitelists:
                raw["whitelists"][url] = get_list(url)
            for url in self.blocklists:
                raw["blocklists"][url] = get_list(url)
        latency = (datetime.utcnow() - start).total_seconds()
        logging.debug(f"blockdata has been updated, elapsed time: {round(latency)}s")
        unified = unifi_lists(raw)
        self.data = unified
        self._ts_updated = datetime.utcnow()
        self._ts_next_update = datetime.utcnow() + timedelta(minutes=self.frequency)
        return unified

    @property
    def blocklisted(self):
        if not self.ready():
            raise NotReady("Block data not ready")
        else:
            return self.data["blocklisted"]

    @property
    def whitelisted(self):
        if not self.ready():
            raise NotReady("Block data not ready")
        else:
            return self.data["whitelisted"]

    @property
    def unified(self):
        """

        :return: all unique domains in blocklists not in whitelists
        :rtype: set
        """
        return self.data["unified"]


def get_list(url):
    logging.debug(f"Fetching {url}")
    entries = set()
    try:
        res = requests.get(url, timeout=30)
    except Exception as e:
        logging.warning(f"Error {e} fetching {url}")
    else:
        if res.status_code == 200:
            logging.debug(f"Processing {url}")
            for entry in parse_list_content(res.content):
                entries.add(entry)
        else:
            logging.warning(f"Failed to fetch {url} - HTTP Status {res.status_code}")
    return entries if entries else None


def parse_list_content(content):
    for line in content.splitlines():
        if not line.startswith(b"#"):
            if line:
                yield line


def unifi_lists(data):
    data["whitelisted"] = set()
    data["blocklisted"] = set()
    for url in data["whitelists"]:
        if data["whitelists"][url]:
            data["whitelisted"].update(data["whitelists"][url])
    for url in data["blocklists"]:
        if data["blocklists"][url]:
            data["blocklisted"].update(data["blocklists"][url])
    data["unified"] = data["blocklisted"].difference(data["whitelisted"])
    return data
