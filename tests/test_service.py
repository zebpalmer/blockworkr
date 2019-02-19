from blockworkr.service import SVCObj, SVC


TEST_CONFIG = {
    "frequency": 24,
    "configz_enabled": True,
    "metricsz_enabled": True,
    "memcached_server": False,
    "combinations": {
        "standard": {
            "whitelists": ["https://zebpalmer.github.io/dns_blocklists/whitelist.txt"],
            "blocklists": [
                "https://zebpalmer.github.io/dns_blocklists/slim.txt",
                "https://zebpalmer.github.io/dns_blocklists/blocklist.txt",
                "http://example.com/404-fake.txt",
            ],
        },
        "slim": {
            "whitelists": ["https://zebpalmer.github.io/dns_blocklists/whitelist.txt"],
            "blocklists": [
                "https://zebpalmer.github.io/dns_blocklists/slim.txt",
                "https://zebpalmer.github.io/dns_blocklists/blocklist.txt",
            ],
        },
    },
}


def test_svc():
    svc = SVC(cfg=TEST_CONFIG)
