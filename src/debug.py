import logging
from richcolorlog import setup_logging

debug_enabled = False
logger = logging.getLogger("scoreboard")
logger.propagate = False

def setup_logger(loglevel='INFO', debug=False,logtofile=False):
    """Sets up the logger."""
    global logger
    level = loglevel
    show_path = False
    if debug:
        level = 'DEBUG'
        show_path = True

    # setup_logging from richcolorlog configures the logger instance
    logger = setup_logging(
        name="scoreboard",
        level=level,
        show_path=show_path,
        show_locals=True,
        rich_tracebacks=True,
        omit_repeated_times=False,
        log_file=logtofile,
        log_file_name="scoreboard.log",
        show=True
    )
    logger.propagate = False


def set_debug_status(config, loglevel='INFO',logtofile=False):
    """Sets the debug status and reconfigures the logger."""
    global debug_enabled
    debug_enabled = config.debug
    if loglevel.lower() == "debug":
        debug_enabled = True

    setup_logger(loglevel, debug_enabled,logtofile)

    if debug_enabled:
        logger.debug("Debug logging enabled")
    else:
        getattr(logger, loglevel.lower())(f"Logging level set to: {loglevel}")
