from blockworkr import __version__, Block


class SVCObj:
    """
    A common object to allow access to services
    """

    svc = None


class SVC:
    def __init__(self):
        self.__version__ = __version__
        self.blockr = Block()
