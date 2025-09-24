import time
import sys
import logging
from richcolorlog import setup_logging

debug_enabled = False


newlogger = setup_logging(show_path=False,show_locals=True,rich_tracebacks=True,omit_repeated_times=False,level=logging.INFO)
newlogger.propagate = False


def set_debug_status(config,loglevel='INFO'):
	global debug_enabled	
	
	debug_enabled = config.debug
	
	if loglevel.lower() == "debug":
		debug_enabled = True

	if debug_enabled:
		newlogger = setup_logging(show=True,show_path=True,show_locals=True,rich_tracebacks=True,omit_repeated_times=False,level='DEBUG')
		newlogger.debug("Debug logging enabled")
	else:
		newlogger = setup_logging(show=True,name="scoreboard",show_path=False,show_locals=True,rich_tracebacks=True,omit_repeated_times=False,level=loglevel)
		getattr(newlogger, loglevel.lower())("Logging level set to: {}".format(loglevel))
	


def __debugprint(text):
	print(text)
	sys.stdout.flush()

def log(text):
	if debug_enabled:
		newlogger.debug(text)

def critical(text):
	newlogger.critical(text,stack_info=True)

def exception(text,e):
  newlogger.exception(text,exc_info=e)

def warning(text):
  newlogger.warning(text)

def error(text):
	newlogger.error(text)

def info(text):
	newlogger.info(text)

def __timestamp():
	return time.strftime("%H:%M:%S", time.localtime())
