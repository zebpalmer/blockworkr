TEST_WHITELISTS = ['https://zebpalmer.github.io/dns_blocklists/whitelist.txt',]
TEST_BLOCKLISTS = ['https://zebpalmer.github.io/dns_blocklists/blocklist.txt',]

from blockworkr.block import Block


def test_block_update():
    b = Block()