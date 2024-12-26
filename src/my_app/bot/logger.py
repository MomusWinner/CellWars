import logging.config
import yaml

with open("src/my_app/config/logging.conf.yml", "r") as f:
    LOGGING_CONFIG = yaml.full_load(f)


class ConsoleFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        return super().format(record)


logger = logging.getLogger("bot_logger")
logger.addFilter(CorrelationFilter())
