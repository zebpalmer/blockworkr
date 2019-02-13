import logging


def setup_logging(name=None, loglevel=None, override_root=True, local_log=True):
    """
    This method should probably be deprecated in the long run,
    but mimics the general setup method for most old halo apps.
    It is needed to facilitate transition.

    :param name: Facility Name
    :param loglevel: Log Level
    :param local_log: (True) If False, will not log locally to file/stdout.
    :return: logger
    """
    if not name:
        raise Exception("Must set desired logging facility name")
    for m in ["requests", "paste", "apscheduler", "werkzeug"]:
        logging.getLogger(m).setLevel(logging.WARNING)

    log = logging.getLogger(name)
    if not loglevel:
        loglevel = "DEBUG"

    log.setLevel(loglevel)
    if not len(log.handlers):
        logformat = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] (%(threadName)-10s) %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )
        if local_log:
            # adding local logger
            stream = logging.StreamHandler()
            stream.setFormatter(logformat)
            log.addHandler(stream)
        # send logs to graypy if host and port are provided
    if override_root:
        # py3 root logger behaves a bit different
        root = logging.getLogger()
        root.handlers = []
        logging.root = log
    logging.info("Initialized {} Logging at {}".format(name, loglevel))
    return log
