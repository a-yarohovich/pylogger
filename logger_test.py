from logger import Logger

LOG = Logger.instance()

def test0(msg):
    try:
        test1(msg)
    except Exception as ex:
        LOG.error("error")

def test1(msg):
    #LOG.debug(msg)
    raise Exception(msg)

test0("hello world!")