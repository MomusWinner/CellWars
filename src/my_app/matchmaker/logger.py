import logging.config
from contextvars import ContextVar

import yaml

with open("src/my_app/config/logging.conf.yml", "r") as f:
    LOGGING_CONFIG = yaml.full_load(f)


class ConsoleFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        return super().format(record)


class CorrelationFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.corr_id = "%s" % correlation_id_ctx.get(None)
        return True


correlation_id_ctx: ContextVar[str] = ContextVar("correlation_id")

logger = logging.getLogger("matchmaker_logger")
logger.addFilter(CorrelationFilter())
