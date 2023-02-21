'''OBS integration plugin'''

# to use this handler, run:
#    sudo apt-get install obsws_python
#    sudo pip install obsws_python

import logging
logger = logging.getLogger(__name__)
import Config
from eventmanager import Evt
from monotonic import monotonic
import importlib
import gevent.monkey

obs = {}
SOCKET_IO = None
MODULE = 'OBS_WS'
time_before_start_ms = 0

class NoOBSManager():
    def __init__(self):
        pass

    def isEnabled(self):
        return False

    def start(self):
        return True

    def stop(self):
        return True

class OBSManager():
    rc = None
    obsModule = None
    config = {} 
    
    def __init__(self, config, obsModule):
        self.config=config
        self.obsModule = obsModule
        self.connect()
        
    def connect(self):
        try:        
            logger.info("OBS: (Re)connecting...")
            self.rc = self.obsModule.ReqClient(host=self.config['HOST'], port=self.config['PORT'], password=self.config['PASSWORD'])        
        except:
            logger.error("OBS: Error connecting to configured instance")


    def isEnabled(self):
        return True

    def start(self):
        try:
            self.rc.start_record()
            logger.info("OBS: Recording Started")
        except:
            self.connect()          
            try:
                self.rc.start_record()
                logger.info("OBS: Recording Started")
            except:
                logger.error("OBS: Start Recording Failed")
                return False    
        return True

    def stop(self):
        try:
            self.rc.stop_record()
            logger.info("OBS: Recording Stoppped")
        except:
            self.connect()          
            try:
                self.rc.stop_record()
                logger.info("OBS: Recording Stoppped")
            except:
                logger.error("OBS: Stop Recording Failed")
                return False
        return True


def emite_priority_message(message, interrupt = False):
    ''' Emits message to clients '''
    emit_payload = {
        'message': message,
        'interrupt': interrupt
    }
    SOCKET_IO.emit('priority_message', emit_payload)


def do_ObsInitialize_fn(args):
    ''' Initialize OBS connection '''
    logger.info("def do_ObsInitialize_fn" )
    global obs, time_before_start_ms
    obs = NoOBSManager()
    if MODULE in Config.ExternalConfig:
        if      'HOST' in Config.ExternalConfig  [MODULE]         \
            and 'PORT' in Config.ExternalConfig  [MODULE]         \
            and 'PASSWORD' in Config.ExternalConfig  [MODULE]     \
            and 'ENABLED' in Config.ExternalConfig  [MODULE]      \
            and Config.ExternalConfig [MODULE]['ENABLED'] == True:
            try:
                obsModule = importlib.import_module('obsws_python')
                obs = OBSManager(config=Config.ExternalConfig  [MODULE], obsModule=obsModule)
            except ImportError:
                logger.error("OBS: Error importing obsws_python, please pip install this library manually")
                obs = NoOBSManager()
                emite_priority_message('Error conneting OBS server', True)
        if 'PRE_START' in Config.ExternalConfig [MODULE]:
            time_before_start_ms = Config.ExternalConfig [MODULE]['PRE_START'] 

    logger.info("def do_ObsInitialize_fn DONE" )

def do_race_start(args):
    logger.info("def do_race_start()")
    if not obs.start():
        emite_priority_message("OBS: Start Recording Failed")


def do_race_stop(args):
    logger.info("def do_race_stop()")
    if not obs.stop():
        emite_priority_message("OBS: Stop Recording Failed")


def do_race_stage(args):
    logger.info("def do_race_stage")
    #wait to before start
    while (monotonic() < args['pi_starts_at_s'] - (time_before_start_ms/1000)):
        gevent.sleep(0.1)
    do_race_start(args)


def initialize(**kwargs):
    global SOCKET_IO
    SOCKET_IO = kwargs['SOCKET_IO']
    if 'Events' in kwargs:
        kwargs['Events'].on(Evt.STARTUP, 'ObsInitialize', do_ObsInitialize_fn, {}, 103 ) # Non block
        #kwargs['Events'].on(Evt.RACE_START, 'ObsRaceStart', do_race_start, {}, 101 ) # Non block
        kwargs['Events'].on(Evt.RACE_STOP, 'ObsRaceStop', do_race_stop, {}, 102 )   # Non block
        kwargs['Events'].on(Evt.RACE_STAGE, 'ObsRaceStage', do_race_stage, {}, 102 )   # Non block
