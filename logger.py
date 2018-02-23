import logging
import os
import json
from logging.handlers import RotatingFileHandler
from configparser import ConfigParser
import traceback


# noinspection PyBroadException
class Logger:
    _instance = None
    _conf_filename = "logger.cfg"

    def __init__(self, conf_path):
        self.log = None
        self.log_file_handler = None
        self.reload_config(conf_path)

    def reload_config(self, conf_path):
        if not conf_path:
            raise ValueError("Try to init logger by empty config path")
        if self.log and self.log.hasHandlers():
            self.log.handlers.clear()
        config = ConfigParser()
        config.read(conf_path + self._conf_filename)
        self.log, self.log_file_handler = Logger._reinit_logger(config)

    @staticmethod
    def instance():
        if not Logger._instance:
            Logger._instance = Logger(os.path.dirname(os.path.realpath(__file__)))
        return Logger._instance

    @staticmethod
    def funcname() -> str:
        return traceback.extract_stack(None, 2)[0][2]

    @staticmethod
    def exmsg(exception) -> str:
        """
        :param exception: exception which need to convert to str
        :return: message from exception
        :exception: safe
        """
        msg = str(exception)
        class_type = str(type(exception))
        return (class_type + " :: " + msg) if msg else class_type

    @staticmethod
    def tojson(obj, sort_keys=False, indent=2) -> str:
        try:
            if type(obj) is str:
                return json.dumps(json.loads(obj), sort_keys=sort_keys, indent=indent)
            else:
                return json.dumps(obj, sort_keys=sort_keys, indent=indent)
        except Exception as ex:
            print("Logger has faired a exception: {}".format(LOG.exmsg(ex)))
            return str(obj)

    def debug(self, msg, filepath_print_stack_level=-3, max_symbols=0, *args, **kwargs) -> None:
        """
        :param max_symbols: max symbols to print
        :param msg: message for print in log
        :param filepath_print_stack_level: param which define a level of stack for printing filename, line and funkname
        level must be negative, for example : -2, -5. Default value is -3
        :exception: safe
        """
        try:
            self.log.log(
                logging.DEBUG,
                self._formatting_msg(msg, filepath_print_stack_level, max_symbols),
                *args,
                **kwargs
            )
        except Exception as ex:
            print("Logger has faired a exception: {}".format(LOG.exmsg(ex)))

    def info(self, msg, filepath_print_stack_level=-3, max_symbols=0, *args, **kwargs) -> None:
        """
        :param msg:
        :param filepath_print_stack_level:
        :param max_symbols:
        :param args:
        :param kwargs:
        :return:
        :exception: safe
        """
        try:
            self.log.log(
                logging.INFO,
                self._formatting_msg(msg, filepath_print_stack_level, max_symbols),
                *args,
                **kwargs
            )
        except Exception as ex:
            print("Logger has faired a exception: {}".format(LOG.exmsg(ex)))

    def warning(self, msg, filepath_print_stack_level=-3, max_symbols=0, *args, **kwargs) -> None:
        """
        :param msg:
        :param filepath_print_stack_level:
        :param max_symbols:
        :param args:
        :param kwargs:
        :return:
        :exception: safe
        """
        try:
            self.log.log(
                logging.WARNING,
                self._formatting_msg(msg, filepath_print_stack_level, max_symbols),
                *args,
                **kwargs
            )
        except Exception as ex:
            print("Logger has faired a exception: {}".format(LOG.exmsg(ex)))

    def error(self, msg, filepath_print_stack_level=-3, max_symbols=0, *args, **kwargs) -> None:
        """
        :param msg:
        :param filepath_print_stack_level:
        :param max_symbols:
        :param args:
        :param kwargs:
        :return:
        :exception: safe
        """
        try:
            self.log.log(
                logging.ERROR,
                self._formatting_msg(msg, filepath_print_stack_level, max_symbols) + "\n" + traceback.format_exc(),
                *args,
                **kwargs
            )
        except Exception as ex:
            print("Logger has faired a exception: {}".format(LOG.exmsg(ex)))

    def critical(self, msg, filepath_print_stack_level=-3, max_symbols=0, *args, **kwargs) -> None:
        """
        :param msg:
        :param filepath_print_stack_level:
        :param max_symbols:
        :param args:
        :param kwargs:
        :return:
        :exception: safe
        """
        try:
            self.log.log(
                logging.CRITICAL,
                self._formatting_msg(msg, filepath_print_stack_level, max_symbols) + "\n" + traceback.format_exc(),
                *args,
                **kwargs
            )
        except Exception as ex:
            print("Logger has faired a exception: {}".format(LOG.exmsg(ex)))

    @staticmethod
    def _reinit_logger(config):
        # create logger
        log_formatter = logging.Formatter("%(levelname)s %(asctime)s.%(msecs)03d %(message)s", "%d.%m %H:%M:%S")
        log = logging.getLogger(config.get("Logger", "name", fallback="default"))
        log.setLevel(logging.INFO)
        # Set up file handler for logger
        filename = __file__ + ".log"
        path: list = filename.split("/")
        path.insert(-1, "logs")
        if path:
            filename = "/".join(path)
            os.makedirs(os.path.dirname(filename), exist_ok=True)
        log_file_handler = RotatingFileHandler(filename=filename,
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
        # Printing config
        for section in config.sections():
            log.log(
                logging.INFO,
                "{0}:{1}".format(section, dict({item[0]: item[1] for item in config.items(section)}))
            )
        return log, log_file_handler

    @staticmethod
    def _formatting_msg(msg, filepath_stack_level, max_symbols) -> str:
        # Get path and filename without full path
        try:
            stack = traceback.extract_stack()
            filepath = stack[filepath_stack_level][0]
            filename = filepath.split('/')[-1]
            line_number = stack[filepath_stack_level][1]
            funcname = stack[filepath_stack_level][2]
            if max_symbols:
                msg = msg[:max_symbols]
            msg = "[" + filename + "] " + msg + " " + "(from " + filepath + " in `" + funcname + "`" + " +" + str(line_number) + ")"
        except Exception as ex:
            print("Logger has faired a exception: {}".format(LOG.exmsg(ex)))
        return msg


# Use this global object for accessing to logger
LOG = Logger.instance()


if __name__ == '__main__':
    def test0(msg):
        test1(msg)

    def test1(msg):
        test2(msg)

    def test2(msg):
        LOG.debug(msg, max_symbols=6)

    test0("testtt")
    LOG.reload_config("/home/andrew/dev/my-capp/logger")
    test0("after")
