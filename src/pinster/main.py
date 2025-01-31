"""Main pinster module."""

import logging
import logging.config

import pinster.logger

logger = logging.getLogger("pinster")


def main() -> None:
    """Main entry point."""
    pinster.logger.setup_logging()
    logger.debug("debug msg", extra={"attr": "HELLO"})
    logger.info("debug msg")
    logger.warning("warning msg")
    logger.error("error msg")
    logger.critical("critical msg")
    try:
        _ = 1 / 0
    except ZeroDivisionError:
        logger.exception("exception msg")


if __name__ == "__main__":
    main()
