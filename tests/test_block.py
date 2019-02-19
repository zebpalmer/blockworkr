import logging
from unittest import mock
from blockworkr import Block
from blockworkr.block import get_list, unifi_lists, all_lists
from blockworkr.service import SVC, SVCObj
from .test_data import *


def test_block_update():
    b = Block(cfg=TEST_CONFIG, cron=False)
    b.update(background=False)
    b.unified("standard")


def test_block_get_list():
    for url in TEST_BLOCKLISTS + TEST_WHITELISTS:
        res = get_list(url)


def test_unifi_lists():
    test_data = {
        "whitelists": {"test1": set(["a", "c", "d", "e", "g"]), "test2": set(["b", "d", "e", "f"])},
        "blocklists": {"block1": set(["d", "e", "f", "g", "x", "z"]), "block2": set(["d", "e", "f", "g", "y", "z"])},
    }
    desired = set(["x", "y", "z"])
    whitelisted, blocklisted, unified = unifi_lists(test_data)
    assert desired == unified


def test_all_lists():
    res = all_lists(TEST_CONFIG)
    desired = set(TEST_BLOCKLISTS) | set(TEST_WHITELISTS)
    assert res == desired


def test_caching():
    with mock.patch("blockworkr.service.MemClient", new=MemMock) as mc:
        SVCObj.svc = SVC(cfg=TEST_BLOCK_MEMCACHE)
        b = Block(SVCObj.svc.cfg, cron=False)
        b.update(background=False)
        b.update(background=False)


class MemMock:
    def __init__(self, *args, **kwargs):
        self._cachedata = {}
        print("MemMock INIT")

    def set(self, key, value, expire=0):
        print(f"Setting {key}")
        self._cachedata[key] = value

    def get(self, key):
        cached = self._cachedata.get(key)
        if cached is not None:
            print(f"Found cache entry for {key}")

        return self._cachedata.get(key)
