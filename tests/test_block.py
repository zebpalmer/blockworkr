from blockworkr import Block
from blockworkr.block import get_list, unifi_lists, all_lists
from blockworkr.service import SVC, SVCObj

TEST_WHITELISTS = ["https://zebpalmer.github.io/dns_blocklists/whitelist.txt"]
TEST_BLOCKLISTS = ["https://zebpalmer.github.io/dns_blocklists/blocklist.txt"]

TEST_CFG = {
    "frequency": 24,
    "combinations": {"standard": {"whitelists": TEST_WHITELISTS, "blocklists": TEST_BLOCKLISTS}},
}

TEST_CONFIG_EXT = {
    "frequency": 24,
    "combinations": {
        "standard": {
            "whitelists": ["https://zebpalmer.github.io/dns_blocklists/whitelist.txt"],
            "blocklists": [
                "https://zebpalmer.github.io/dns_blocklists/blocklist.txt",
                "https://mirror1.malwaredomains.com/files/justdomains",
                "http://sysctl.org/cameleon/hosts",
                "https://hosts-file.net/ad_servers.txt",
            ],
        }
    },
}


def test_block_update():
    b = Block(cfg=TEST_CFG, cron=False)
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
    res = all_lists(TEST_CFG)
    desired = set(TEST_BLOCKLISTS) | set(TEST_WHITELISTS)
    assert res == desired
