from blockworkr import Block
from blockworkr.block import get_list, unifi_lists

TEST_WHITELISTS = ["https://zebpalmer.github.io/dns_blocklists/whitelist.txt"]
TEST_BLOCKLISTS = ["https://zebpalmer.github.io/dns_blocklists/blocklist.txt"]


def test_block_update():
    b = Block(blocklists=TEST_BLOCKLISTS, whitelists=TEST_WHITELISTS)
    b.update(background=False)
    b.blocklists
    b.blocklisted
    b.whitelists
    b.whitelisted
    b.unified


def test_block_get_list():
    for url in TEST_BLOCKLISTS + TEST_WHITELISTS:
        res = get_list(url)


def test_unifi_lists():
    test_data = {
        "whitelists": {"test1": set(["a", "c", "d", "e", "g"]), "test2": set(["b", "d", "e", "f"])},
        "blocklists": {"block1": set(["d", "e", "f", "g", "x", "z"]), "block2": set(["d", "e", "f", "g", "y", "z"])},
    }
    desired = set(["x", "y", "z"])
    assert desired == unifi_lists(test_data)["unified"]
