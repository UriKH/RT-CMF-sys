from dataclasses import dataclass, fields

from .configurable import Configurable


@dataclass
class LogConfig(Configurable):
    SLEEP_TO_PRINT: bool = False
    PROFILE: bool = False
    PROFILE_SUMMARY: bool = False
    GENERATE_LOGS: bool = True
    LOG_FILENAME: str = "run.log"
    EXCEPTION_SHOW_TRACE: bool = False
    DEBUG_SHOW_TRACE: bool = False



logging_config: LogConfig = LogConfig()
