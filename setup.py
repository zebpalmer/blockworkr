import os
import re
from setuptools import setup, find_packages

with open("VERSION") as vf:
    __version__ = vf.readline().strip()

__desc__ = "Blockworkr"

if os.path.exists("./requirements.txt"):
    with open("./requirements.txt", "r") as reqs:
        __requirements__ = [x.strip() for x in reqs.readlines() if not x.startswith("--")]
else:
    raise Exception("Missing requirements.txt")

re_strip_version = re.compile(r"(\w*)")


def strip_version(req):
    return re_strip_version.match(req).groups()[0].lower()


setup(
    name="blockworkr",
    version=__version__,
    author="Zeb Palmer",
    author_email="zeb@zebpalmer.com",
    url="https://github.com/zebpalmer/blockworkr",
    scripts=["scripts/blockworkr-ws"],
    install_requires=__requirements__,
    description=__desc__,
    packages=find_packages(exclude=("tests",)),
)
