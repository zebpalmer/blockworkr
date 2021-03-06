import os
import yaml
from pathlib import Path
from blockworkr import __version__
from pymemcache.client.base import Client as MemClient
from pymemcache import serde


class SVCObj:
    """
    A common object to allow access to services
    """

    svc = None


class SVC:
    def __init__(self, config_file=None, cfg=None):
        self.__version__ = __version__
        self._config_file = config_file
        if cfg:
            self.cfg = cfg
        else:
            self.cfg = self._get_config()
        self.blockr = None
        if self.cfg.get("memcached_server"):
            self.memcache = MemClient(
                (self.cfg["memcached_server"], 11211),
                serializer=serde.python_memcache_serializer,
                deserializer=serde.python_memcache_deserializer,
                timeout=10,
                connect_timeout=10,
            )
        else:
            self.memcache = None

    def _get_config(self):
        if not self._config_file:
            if os.environ.get("CONFIG_FILE", None):
                self._config_file = os.environ["CONFIG_FILE"]
            elif Path("/etc/blockworkr/config.yaml").is_file():
                self._config_file = "/etc/blockworkr/config.yaml"
        if self._config_file:
            with open(self._config_file) as f:
                cfg = yaml.safe_load(f)
        else:
            cfg = {}
            lists = ["WHITELISTS", "BLOCKLISTS"]
            for l in lists:
                # desired config method is via file.
                # but if user has simple setup, w/ one config
                # go ahead and setup a single combo entry 'unified'
                # with their desired lists
                if os.environ.get(l):
                    cfg["unified"][l.lower()] = os.environ[l].split(",")
            props = ["FREQUENCY", "DISK_CACHE"]
            for prop in props:
                if os.environ.get(prop, None):
                    cfg[prop.lower()] = os.environ[prop]
        return cfg
