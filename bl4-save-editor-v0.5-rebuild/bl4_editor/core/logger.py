import logging, os, glob, time
from datetime import datetime
from bl4_editor.core import settings
LOG_DIR = os.path.join(os.getcwd(), "logs")
os.makedirs(LOG_DIR, exist_ok=True)
# cleanup old logs once at startup
retention_minutes = settings.get_setting("log_retention_minutes", 10)
try:
    cutoff = time.time() - (int(retention_minutes) * 60)
    for p in glob.glob(os.path.join(LOG_DIR, "debug_*.log")):
        try:
            if os.path.getmtime(p) < cutoff:
                os.remove(p)
        except Exception:
            pass
except Exception:
    pass
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
LOG_FILE = os.path.join(LOG_DIR, f"debug_{timestamp}.log")
logger = logging.getLogger("BL4SaveEditor")
logger.setLevel(logging.DEBUG)
# file handler
fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
fh.setLevel(logging.DEBUG)
fmt = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
fh.setFormatter(fmt)
logger.addHandler(fh)
# console handler
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(fmt)
logger.addHandler(ch)
_debug_tab = None
def set_debug_tab(tab):
    global _debug_tab
    _debug_tab = tab
def _push_to_tab(level, msg):
    if _debug_tab:
        try:
            _debug_tab.append_log(level.lower(), msg)
        except Exception:
            pass
def debug(msg):
    logger.debug(msg)
    _push_to_tab("debug", msg)
def info(msg):
    logger.info(msg)
    _push_to_tab("info", msg)
def warning(msg):
    logger.warning(msg)
    _push_to_tab("warning", msg)
def error(msg):
    logger.error(msg)
    _push_to_tab("error", msg)
