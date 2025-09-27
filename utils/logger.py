import functools
import time
import inspect
from enum import Enum, auto


# TODO: Convert from this logger to the "logging" library
class Logger:
    """
    Logging for terminal interface and debugging
    """
    class Levels(Enum):
        message = auto()
        info = auto()
        warning = auto()
        inform = auto()
        exception = auto()
        fatal = auto()

    class Colors:
        white = '\033[0m'
        red = '\033[91m'
        green = '\033[92m'
        yellow = '\033[93m'

    def __init__(self, msg, level=Levels.message, end_with_nl=True, condition=True):
        calling_frame = inspect.stack()[1]
        self.calling_function_name = calling_frame.function
        self.level = level if isinstance(level, Logger.Levels) else Logger.Levels.info
        self.msg = msg
        self.condition = condition
        if end_with_nl:
            self.end = f'{Logger.Colors.white}\n'
        else:
            self.end = f'{Logger.Colors.white} '

    def time_it(self, func):
        """
        Decorator to log the processing time of a function
        :param func: the function to time
        :return: the wrapped function
        """
        @functools.wraps(func)
        def wrapper(*args, **kwarg):
            start = time.time()
            result = func(*args, **kwarg)
            end = time.time()

            if round(end - start, 3) != 0:
                Logger(self.msg + f' - in {(end - start):.3f} seconds', self.level).log()
            return result
        return wrapper

    def log(self, msg_prefix='', in_function: bool = False):
        """
        Log a message with it's logging level to the standard output
        :param msg_prefix: the message level prefix for printing
        """
        if not self.condition:
            return

        match self.level:
            case Logger.Levels.message:  # message
                print(f'{Logger.Colors.white}{msg_prefix}{self.msg}', end=self.end)
            case Logger.Levels.info:       # info - green
                print(f'{Logger.Colors.green}{msg_prefix}[INFO] {self.msg}', end=self.end)
            case Logger.Levels.warning:    # warning - yellow
                print(f'{Logger.Colors.yellow}{msg_prefix}[WARNING] {self.msg}', end=self.end)
            case Logger.Levels.inform:     # does not raise exception - red
                msg = f'{Logger.Colors.red}{msg_prefix}[NOTICE] {self.msg}'
                if in_function:
                    msg += f' in {self.calling_function_name}'
                print(msg, end=self.end)
            case Logger.Levels.exception:  # exception - red
                msg = f'{Logger.Colors.red}{msg_prefix}[ERROR] {self.msg}'
                if in_function:
                    msg += f' in {self.calling_function_name}'
                print(msg, end=self.end)
            case Logger.Levels.fatal:      # fatal error - red
                print(f'{Logger.Colors.red}{msg_prefix}[ERROR] {self.msg} in {self.calling_function_name} \n\t'
                      f'-> exiting', end=self.end)
                try:
                    __IPYTHON__
                    raise Exception('Stopping...')
                except NameError:
                    exit(1)
        return

    @staticmethod
    def log_exec(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            Logger(f'executing {func.__name__}', Logger.Levels.info).log()
            return func(*args, **kwargs)
        return wrapper

