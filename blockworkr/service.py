import os
import yaml
from pathlib import Path
from blockworkr import __version__, Block


class SVCObj:
    """
    A common object to allow access to services
    """

    svc = None


class SVC:
    def __init__(self):
        self.__version__ = __version__
        self.cfg = self._get_config()
        self.blockr = Block(
            blocklists=self.cfg.get("blocklists"),
            whitelists=self.cfg.get("whitelists"),
            frequency=self.cfg.get("frequency", 24),
            disk_cache=self.cfg.get("disk_cache", False),
        )

    def _get_config(self):
        if os.environ.get("CONFIG_FILE", None):
            config_file = os.environ['CONFIG_FILE']
        elif Path("/etc/blockworkr/config.yaml").is_file():
            config_file = "/etc/blockworkr/config.yaml"
        if config_file:
            with open(config_file) as f:
                cfg = yaml.safe_load(f)
        else:
            cfg = {}
            split = ["WHITELISTS", "BLOCKLISTS"]
            props = ["WHITELISTS", "BLOCKLISTS", "FREQUENCY", "DISK_CACHE"]
            for prop in props:
                if os.environ.get(prop, None):
                    if prop in split:
                        cfg[prop.lower()] = os.environ[prop].split(",")
                    else:
                        cfg[prop.lower()] = os.environ[prop]
        return cfg
