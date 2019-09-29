TEST_WHITELISTS = ["https://zebpalmer.github.io/dns_blocklists/whitelist.txt"]
TEST_BLOCKLISTS = [
    "https://zebpalmer.github.io/dns_blocklists/blocklist.txt",
    "https://zebpalmer.github.io/dns_blocklists/slim.txt",
    "https://httpbin.org/status/404",
]

TEST_BLOCK_MEMCACHE = {
    "frequency": 24,
    "configz_enabled": True,
    "metricsz_enabled": True,
    "memcached_server": "memcched",
    "combinations": {
        "standard": {
            "whitelists": ["https://zebpalmer.github.io/dns_blocklists/whitelist.txt"],
            "blocklists": [
                "https://zebpalmer.github.io/dns_blocklists/slim.txt",
                "https://zebpalmer.github.io/dns_blocklists/blocklist.txt",
                "https://httpbin.org/status/404",
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


TEST_CONFIG = {
    "frequency": 24,
    "memcached_server": False,
    "combinations": {
        "standard": {
            "whitelists": ["https://zebpalmer.github.io/dns_blocklists/whitelist.txt"],
            "blocklists": [
                "https://zebpalmer.github.io/dns_blocklists/slim.txt",
                "https://zebpalmer.github.io/dns_blocklists/blocklist.txt",
                "https://httpbin.org/status/404",
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
