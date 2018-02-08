import logging
import os
import json
from logging.handlers import RotatingFileHandler
from configparser import ConfigParser
import traceback


# noinspection PyBroadException
class Logger:
    __instance = None

    def __init__(self, config_file_name):
        config = ConfigParser()
        config.read(config_file_name)
        self.log, self.log_file_handler = Logger._init_logger(config)

    @staticmethod
    def instance():
        if not Logger.__instance:
            Logger.__instance = Logger(os.path.dirname(os.path.realpath(__file__)) + '/logger.cfg')
        return Logger.__instance

    @staticmethod
    def funcname():
        return traceback.extract_stack(None, 2)[0][2]

    @staticmethod
    def exmsg(exception) -> str:
        msg = str(exception)
        class_type = str(type(exception))
        return (class_type + " :: " + msg) if msg else class_type

    def debug(self, msg, filepath_print_stack_level=-3, max_symbols=0, *args, **kwargs) -> None:
        """
        :param max_symbols: max symbols to print
        :param msg: message for print in log
        :param filepath_print_stack_level: param which define a level of stack for printing filename, line and funkname
        level must be negative, for example : -2, -5. Default value is -3
        """
        content_type = kwargs.pop("content_type", None)
        if content_type == "json":
            msg = json.dumps(msg, sort_keys=False, indent=2)
        self.log.log(logging.DEBUG, self._formatting_msg(msg, filepath_print_stack_level, max_symbols), *args, **kwargs)

    def info(self, msg, filepath_print_stack_level=-3, max_symbols=0, *args, **kwargs) -> None:
        self.log.log(logging.INFO, self._formatting_msg(msg, filepath_print_stack_level, max_symbols), *args, **kwargs)

    def warning(self, msg, filepath_print_stack_level=-3, max_symbols=0, *args, **kwargs) -> None:
        self.log.log(logging.WARNING, self._formatting_msg(msg, filepath_print_stack_level, max_symbols), *args,
                     **kwargs)

    def error(self, msg, filepath_print_stack_level=-3, max_symbols=0, *args, **kwargs) -> None:
        self.log.log(
            logging.ERROR,
            self._formatting_msg(msg, filepath_print_stack_level, max_symbols) + "\n" + traceback.format_exc(),
            *args,
            **kwargs
        )

    def critical(self, msg, filepath_print_stack_level=-3, max_symbols=0, *args, **kwargs) -> None:
        self.log.log(
            logging.CRITICAL,
            self._formatting_msg(msg, filepath_print_stack_level, max_symbols) + "\n" + traceback.format_exc(),
            *args,
            **kwargs
        )

    @staticmethod
    def _init_logger(config):
        # create logger
        log_formatter = logging.Formatter('%(levelname)s %(thread)d %(asctime)s %(message)s')
        log = logging.getLogger('my-capp')
        log.setLevel(logging.INFO)
        # Set up file handler for logger
        log_file_handler = RotatingFileHandler(filename=__file__ + ".log",
                                               maxBytes=config.getint("Logger", "max_bytes", fallback=100000000),
                                               backupCount=config.getint("Logger", "backup_count", fallback=5))
        log_file_handler.setFormatter(log_formatter)
        log.addHandler(log_file_handler)
        # Set up console handler for logger
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(log_formatter)
        log.addHandler(console_handler)
        if config.getboolean("Logger", "verbose", fallback=True):
            log.setLevel(logging.DEBUG)
        return log, log_file_handler

    @staticmethod
    def _formatting_msg(msg, filepath_stack_level, max_symbols):
        # Get path and filename without full path
        try:
            stack = traceback.extract_stack()
            filepath = stack[filepath_stack_level][0]
            filename = filepath.split('/')[-1]
            line_number = stack[filepath_stack_level][1]
            funcname = stack[filepath_stack_level][2]
            if max_symbols:
                msg = msg[:max_symbols]
            msg = msg + " " + "(from " + filepath + " in `" + funcname + "`" + " +" + str(line_number) + ")"
        except:
            pass
        return msg


# ---------------------------------------------------------------------

# Use this global object for accessing to logger
LOG = Logger.instance()

if __name__ == '__main__':
    def test0(msg):
        test1(msg)


    def test1(msg):
        test2(msg)


    def test2(msg):
        LOG.debug(msg, max_symbols=6)


    ex = None
    try:
        raise ValueError("Test")
    except Exception as ex:
        LOG.warning(LOG.exmsg(ex))

        # test0("hello world!")
