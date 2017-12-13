import logging
import os
from logging.handlers import RotatingFileHandler
from configparser import ConfigParser
import traceback

# ---------------------------------------------------------------------

class Logger:
    __instance = None

    @staticmethod
    def instance():
        if Logger.__instance == None:
            Logger.__instance = Logger(os.path.dirname(os.path.realpath(__file__)) + '/logger.cfg')
        return Logger.__instance

    def __init__(self, config_file_name):
        config = ConfigParser()
        config.read(config_file_name)
        self.log, self.log_file_handler = Logger.init_logger(config)

    @staticmethod
    def init_logger(config):
        # create logger
        log_formatter = logging.Formatter('%(levelname)s %(thread)d %(asctime)s %(message)s')
        log = logging.getLogger('my-capp')
        log.setLevel(logging.INFO)
        # Set up file handler for logger
        log_file_handler = RotatingFileHandler(filename=__file__ + ".log",
                                               maxBytes=config.getint("Logger", "max_bytes"),
                                               backupCount=config.getint("Logger", "backup_count"))
        log_file_handler.setFormatter(log_formatter)
        log.addHandler(log_file_handler)
        # Set up console handler for logger
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(log_formatter)
        log.addHandler(console_handler)
        if config.getboolean("Logger", "verbose"):
            log.setLevel(logging.DEBUG)
        return log, log_file_handler

    def __formatting_msg(self, msg):
        stack = traceback.extract_stack()
        # Get path and filename without full path
        filepath = stack[-3][0]
        filename = filepath.split('/')[-1]
        line_number = stack[-3][1]
        funcname = stack[-3][2]
        msg = filename + ":" + str(line_number) + " " + msg + " " + filepath + " in `" + funcname + "`"
        return msg

    def debug(self, msg, *args, **kwargs):
        self.log.log(logging.DEBUG, self.__formatting_msg(msg), *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self.log.log(logging.INFO, self.__formatting_msg(msg), *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self.log.log(logging.WARNING, self.__formatting_msg(msg), *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self.log.log(logging.ERROR, self.__formatting_msg(msg) + "\n" + traceback.format_exc(), *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        self.log.log(logging.CRITICAL, self.__formatting_msg(msg) + "\n" + traceback.format_exc(), *args, **kwargs)


# ---------------------------------------------------------------------

# Use this global object for accessing to logger
LOG = Logger.instance()
