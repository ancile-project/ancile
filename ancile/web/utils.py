from os import kill
import signal
from ancile.web.errors import AncileException

def _get_pid():
    with open('.pidfile') as f:
        return int(f.readline())

def reload_server():
    try:
        kill(_get_pid(), signal.SIGHUP)
    except (FileNotFoundError, ValueError):
        AncileException('Could not reload server')