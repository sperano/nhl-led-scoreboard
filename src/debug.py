import logging
from richcolorlog import setup_logging

debug_enabled = False

def setup_logger(loglevel='INFO', debug=False,logtofile=False):
    """Sets up the logger."""
    global logger
    level = loglevel
    show_path = False
    template = "%(asctime)s | %(levelname)s | %(message)s"
    if debug:
        show_path = True
        level = 'DEBUG'
        # This is broken under richcolorlog 1.44.5 as the function, filename and line only show the richcolorlog 
        # and not the calling python script
        template = "%(asctime)s | %(name)s | %(levelname)s | %(funcName)s() | %(message)s | %(filename)s:%(lineno)d"

    # setup_logging from richcolorlog configures the logger instance
    logger = setup_logging(
        name="scoreboard",
        level=level,
        show_path = show_path,
        show_locals=True,
        show_icon=True,
        rich_tracebacks=True,
        omit_repeated_times=False,
        log_file=logtofile,
        log_file_name="scoreboard.log",
        format_template=template
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
