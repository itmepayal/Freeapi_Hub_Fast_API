import logging
import sys
import os
from loguru import logger
import sentry_sdk

ENV = os.getenv("ENV", "dev")

os.makedirs("logs", exist_ok=True)

# -------------------------
# Base config
# -------------------------
logger.remove()

# Custom level colors
logger.level("INFO", color="<green>")
logger.level("WARNING", color="<yellow>")
logger.level("ERROR", color="<red>")
logger.level("CRITICAL", color="<bold><red>")

# -------------------------
# DEV
# -------------------------
if ENV == "dev":
    logger.add(
        sys.stdout,
        level="DEBUG",
        colorize=True,
        backtrace=False,
        diagnose=False,
        format="<level>{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | "
               "{name}:{function}:{line} | {message}</level>",
    )

# -------------------------
# PROD
# -------------------------
else:
    logger.add(
        "logs/app.log",
        level="INFO",
        serialize=True,
        rotation="100 MB",
        retention="30 days",
        compression="zip",
        enqueue=True,
    )

    sentry_sdk.init(
        dsn="https://4d959715432514f7375a773a7adc17e2@o4510901392310272.ingest.us.sentry.io/4510901395914752",
        send_default_pii=True,
    )

# -------------------------
# Intercept std logging
# -------------------------
class InterceptHandler(logging.Handler):
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        logger.opt(
            depth=6,
            exception=record.exc_info,
        ).log(level, record.getMessage())


logging.root.handlers = [InterceptHandler()]
logging.root.setLevel(logging.INFO)

# Redirect uvicorn logs
for name in list(logging.root.manager.loggerDict.keys()):
    if name.startswith("uvicorn"):
        logging.getLogger(name).handlers = [InterceptHandler()]
        logging.getLogger(name).propagate = False


# export logger
__all__ = ["logger"]
