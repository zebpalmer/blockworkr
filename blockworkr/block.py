import logging
from threading import Lock, Thread
from datetime import datetime, timedelta
from time import sleep
import requests
from prometheus_client import Enum, Summary, Gauge
from .service import SVCObj


class NotReady(Exception):
    pass


# Metrics
blockworkr_data_ready = Enum(
    "blockworkr_data_ready",
    "Tracks blockdata ready state",
    states=["ready", "notready"],
)
blockworkr_data_ready.state("notready")
update_inprogress = Gauge(
    "blockworkr_update_inprogress", "will increment as an update is running"
)


class Block(SVCObj):
    def __init__(self, cfg=None, cron=True):
        if cfg:
            self.cfg = cfg
        self._all_lists = all_lists(cfg)
        self._list_data = None
        self._combinations = {}
        # self.disk_cache = self.cfg.get("disk_cache", None)
        self.frequency = self.cfg.get("Frequency", 24)
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
        dataready = False
        if self._ts_updated:
            dataready = bool(
                self._ts_updated
                > datetime.utcnow() - timedelta(hours=self.frequency * 2)
            )
        if dataready:
            blockworkr_data_ready.state("ready")
        else:
            blockworkr_data_ready.state("notready")
        return dataready

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

    @update_inprogress.track_inprogress()
    def _update_blockdata(self):
        """
        This method updates the data
        Don't call this method directly, use update() or check_update()

        :return: runs an update cycle
        :rtype: dict
        """
        logging.debug("blockdata is updating")
        start = datetime.utcnow()
        with self._update_thread_lock:
            self._list_data = self.get_all_lists_data(self._all_lists)
            fetch_latency = (datetime.utcnow() - start).total_seconds()
            logging.debug(
                f"blocklist data has been retrieved. elapsed time: {round(fetch_latency)}s"
            )
            self._combinations = parse_combinations(
                self.cfg["combinations"], self._list_data
            )
            self._ts_updated = datetime.utcnow()
            self._ts_next_update = datetime.utcnow() + timedelta(hours=self.frequency)
            latency = (datetime.utcnow() - start).total_seconds()
            logging.debug(
                f"blockdata has been updated, elapsed time: {round(latency)}s"
            )
        return True

    def unified(self, combo):
        """

        :return: all unique domains in blocklists not in whitelists
        :rtype: set
        """
        if not self.ready():
            raise NotReady("Block data not ready")
        return self._combinations[combo]["unified"]

    def get_all_lists_data(self, lists):
        res = {}
        cached = None
        stale = None
        for url in lists:
            result = None
            cache_entry = self.get_cached_url(url)
            if cache_entry:
                cached, stale = cache_entry
            if cached and not stale:
                logging.info(f"using cached data for: {url}")
                res[url] = cached
            else:
                try:
                    result = get_list(url)
                except Exception as e:
                    logging.info(f"{e} in get_list: {url}")
                if result:
                    res[url] = result
                    if self.svc.memcache:
                        try:
                            self.set_cached_url(url, result)
                            logging.debug(f"Caching result for {url}")
                        except Exception as e:
                            logging.warning(e)
                else:
                    if cached:  # don't care if it's stale
                        res[url] = cached
        return res

    def get_cached_url(self, url):
        cached = None
        stale = True
        ts = None
        if self.svc and self.svc.memcache:
            try:
                entry = self.svc.memcache.get(url)
                if entry:
                    ts, cached = entry
            except Exception as e:
                logging.warning(f"Error getting url cache: {e}")
            if ts and datetime.utcnow() < ts + timedelta(hours=self.frequency):
                stale = False
            if cached:
                if not stale:
                    logging.debug(f"Found current cache entry for: {url}")
                else:
                    logging.debug(f"Found stale cache entry for: {url}")
            else:
                logging.debug(f"No cache entry found for: {url}")
        return cached, stale

    def set_cached_url(self, url, data):
        if self.svc.memcache:
            try:
                expire = int(timedelta(weeks=1).total_seconds())
                payload = (datetime.utcnow(), data)
                set_res = self.svc.memcache.set(
                    url, payload, expire=expire, noreply=False
                )
                if not set_res:
                    logging.debug(
                        f"Cache set returned {set_res} for {url} with expire {expire}"
                    )
            except Exception as e:
                logging.warning(f"Error setting url cache: {e}")


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
                if b"#" in line:
                    line = line.split(b"#")[0]  # strip any trailing comments
                if b" " in line:
                    line = line.split(b" ")[1]  # handle host files
                if b"\t" in line:
                    line = line.split(b"\t")[1]  # handle host files
                line = line.strip()
                if line:
                    yield line


def unifi_lists(data):
    whitelisted = set()
    blocklisted = set()
    for wlist in data["whitelists"]:
        if data["whitelists"][wlist]:
            whitelisted.update(data["whitelists"][wlist])
    for blist in data["blocklists"]:
        if data["blocklists"][blist]:
            blocklisted.update(data["blocklists"][blist])
    unified = blocklisted.difference(whitelisted)
    return whitelisted, blocklisted, unified


def all_lists(cfg):
    lists = set()
    for combo in cfg.get("combinations", []):
        for ltype in ["whitelists", "blocklists"]:
            for url in cfg["combinations"][combo][ltype]:
                lists.add(url)
    return lists


def parse_combinations(combinations, list_data):
    res = {}
    for combo_name in combinations:
        res[combo_name] = parse_combo(combo_name, combinations[combo_name], list_data)
    return res


def parse_combo(combo_name, config, list_data):
    data = {"whitelists": {}, "blocklists": {}}
    for list_type in ["whitelists", "blocklists"]:
        for url in config.get(list_type, []):
            data[list_type][url] = list_data.get(url, set())
    data["whitelisted"], data["blocklisted"], data["unified"] = unifi_lists(data)
    data["combo_metrics"] = combo_metrics(combo_name, data)
    return data


def combo_metrics(combo_name, data):
    cm = {
        "whitelist_count": sum([len(x) for x in data["whitelists"].values() if x]),
        "blocklist_count": sum([len(x) for x in data["blocklists"].values() if x]),
        "whitelisted_unique": len(data["whitelisted"]),
        "blocklisted_unique": len(data["blocklisted"]),
        "unified_count": len(data["unified"]),
    }
    try:
        update_combo_metrics(combo_name, cm)
    except Exception as e:
        logging.warning(e)
    return cm


def update_combo_metrics(combo_name, cm):
    Gauge(
        f"blockworkr_combo_{combo_name}_whitelist_count",
        f"blockworkr_combo_{combo_name}_whitelist_count",
    ).set(cm["whitelist_count"])
    Gauge(
        f"blockworkr_combo_{combo_name}_blocklist_count",
        f"blockworkr_combo_{combo_name}_blocklist_count",
    ).set(cm["blocklist_count"])
    Gauge(
        f"blockworkr_combo_{combo_name}_whitelisted_unique_count",
        f"blockworkr_combo_{combo_name}_whitelisted_unique_count",
    ).set(cm["whitelisted_unique"])
    Gauge(
        f"blockworkr_combo_{combo_name}_blocklisted_unique_count",
        f"blockworkr_combo_{combo_name}_blocklisted_unique_count",
    ).set(cm["blocklisted_unique"])
    Gauge(
        f"blockworkr_combo_{combo_name}_unified_count",
        f"blockworkr_combo_{combo_name}_unified_count",
    ).set(cm["unified_count"])
