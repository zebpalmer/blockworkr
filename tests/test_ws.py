from blockworkr.service import SVCObj, SVC
from .test_data import *


def test_ws():
    svc = SVC(cfg=TEST_CONFIG)
    SVCObj.svc = svc
    from blockworkr.webservice import ws
