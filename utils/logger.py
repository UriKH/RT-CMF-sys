import time
import inspect


# TODO: Convert from this logger to the "logging" library
class Logger:
    """
    Logging for terminal interface and debugging
    """
    message = 0
    info = 1
    warning = 2
    inform = 3
    exception = 4
    error = 5

    class Colors:
        white = '\033[0m'
        red = '\033[91m'
        green = '\033[92m'
        yellow = '\033[93m'

    def __init__(self, msg, level=message, new_line=True, condition=True):
        calling_frame = inspect.stack()[1]
        self.calling_function_name = calling_frame.function
        self.level = level if level in range(Logger.error + 1) else Logger.info
        self.msg = msg
        self.condition = condition
        if new_line:
            self.end = f'{Logger.Colors.white}\n'
        else:
            self.end = f'{Logger.Colors.white} '

    def time_it(self, func):
        """
        Decorator to log the processing time of a function
        :param func: the function to time
        :return: the wrapped function
        """
        def wrapper(*args, **kwarg):
            start = time.time()
            result = func(*args, **kwarg)
            end = time.time()

            if round(end - start, 3) != 0:
                Logger(self.msg + f' - in {(end - start):.3f} seconds', self.level).log()
            return result
        return wrapper

    def log(self, msg_prefix='> '):
        """
        Log a message with it's logging level to the standard output
        :param msg_prefix: the message level prefix for printing
        """
        if not self.condition:
            return

        match self.level:
            case Logger.message:  # message
                print(f'{Logger.Colors.white}{msg_prefix}{self.msg}', end=self.end)
            case Logger.info:       # info - green
                print(f'{Logger.Colors.green}[INFO] {self.msg}', end=self.end)
            case Logger.warning:    # warning - yellow
                print(f'{Logger.Colors.yellow}[WARNING] {self.msg}', end=self.end)
            case Logger.inform:     # does not raise exception - red
                print(f'{Logger.Colors.red}[EXCEPT/ERROR] {self.msg} in {self.calling_function_name}', end=self.end)
            case Logger.exception:  # exception - red
                raise Exception(f'{Logger.Colors.red}[EXCEPT] {self.msg} in {self.calling_function_name}{self.end}')
            case Logger.error:      # fatal error - red
                print(f'{Logger.Colors.red}[ERROR] {self.msg} in {self.calling_function_name} \n\t'
                      f'-> exiting', end=self.end)
                exit(1)
        return
