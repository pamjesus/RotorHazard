'''OBS integration plugin'''

# to use this handler, run:
#    sudo apt-get install obsws_python
#    sudo pip install obsws_python

import logging
logger = logging.getLogger(__name__)
import traceback
import Config
from eventmanager import Evt
from plugins.rh_obs_control.obs_manager import NoOBSManager, OBSManager
import importlib
#from server import  emit_priority_message                  #FIXME TODO

obs = {}


def do_ObsInitialize_fn(args):
    """Initialize OBS connection"""
    global obs
    logger.info("def do_ObsInitialize_fn(()" )
    obs = NoOBSManager()
    if 'OBS' in Config.GENERAL and 'HOST' in Config.GENERAL['OBS'] and 'PORT' in Config.GENERAL['OBS'] and 'PASSWORD' in Config.GENERAL['OBS']:
        try:
            obsModule = importlib.import_module('obsws_python')
            obs = OBSManager(config=Config.GENERAL['OBS'], obsModule=obsModule)
        except ImportError:
            logger.error("OBS: Error importing obsws_python, please pip install this library manually")
            obs = NoOBSManager()

def do_race_start(args):
    global obs
    logger.info("def do_race_start()")
    if not obs.start():
        pass
        #emit_priority_message("OBS: Start Recording Failed", True)     #TODO

def do_race_stop(args):
    global obs
    logger.info("def do_race_stop()")
    if not obs.stop():
        pass
        #emit_priority_message("OBS: Stop Recording Failed", True)       #TODO

def do_race_event(args):
    print ('Event ', args['event'])

def initialize(**kwargs):
    if 'Events' in kwargs:
        kwargs['Events'].on(Evt.STARTUP, 'ObsInitialize', do_ObsInitialize_fn, {}, 90 )
        kwargs['Events'].on(Evt.RACE_START, 'ObsRaceStart', do_race_start, {}, 101 ) # Bloquer / Non bloquer ?
        kwargs['Events'].on(Evt.RACE_STOP, 'ObsRaceStop', do_race_stop, {}, 102 )   # Bloquer / Non bloquer ?

        kwargs['Events'].on(Evt.RACE_STAGE, 'ObsRace_schedule_stage', do_race_event, {'event': 'RACE_STAGE'}, 101 )
        kwargs['Events'].on(Evt.RACE_FINISH, 'ObsRaceFinish', do_race_event, {'event': 'RACE_FINISH'}, 101 )
