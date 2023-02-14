'''OBS integration plugin'''

# to use this handler, run:
#    sudo apt-get install obsws_python
#    sudo pip install obsws_python

import logging
logger = logging.getLogger(__name__)
import Config
from eventmanager import Evt
from plugins.rh_obs_control.obs_manager import NoOBSManager, OBSManager
import importlib

obs = {}
SOCKET_IO = None


def emite_priority_message(message):
    ''' Emits message to clients '''
    emit_payload = {
        'message': message,
        'interrupt': False
    }
    SOCKET_IO.emit('priority_message', emit_payload)


def do_ObsInitialize_fn(args):
    ''' Initialize OBS connection '''
    logger.info("def do_ObsInitialize_fn(()" )
    global obs
    obs = NoOBSManager()
    if 'OBS' in Config.GENERAL and 'HOST' in Config.GENERAL['OBS'] and 'PORT' in Config.GENERAL['OBS'] and 'PASSWORD' in Config.GENERAL['OBS']:
        try:
            obsModule = importlib.import_module('obsws_python')
            obs = OBSManager(config=Config.GENERAL['OBS'], obsModule=obsModule)
        except ImportError:
            logger.error("OBS: Error importing obsws_python, please pip install this library manually")
            obs = NoOBSManager()


def do_race_start(args):
    logger.info("def do_race_start()")
    if not obs.start():
        emite_priority_message("OBS: Start Recording Failed")


def do_race_stop(args):
    logger.info("def do_race_stop()")
    if not obs.stop():
        emite_priority_message("OBS: Stop Recording Failed")


def initialize(**kwargs):
    global SOCKET_IO
    SOCKET_IO = kwargs['SOCKET_IO']
    if 'Events' in kwargs:
        kwargs['Events'].on(Evt.STARTUP, 'ObsInitialize', do_ObsInitialize_fn, {}, 90 )
        kwargs['Events'].on(Evt.RACE_START, 'ObsRaceStart', do_race_start, {}, 101 ) # Bloquer / Non bloquer ?
        kwargs['Events'].on(Evt.RACE_STOP, 'ObsRaceStop', do_race_stop, {}, 102 )   # Bloquer / Non bloquer ?
