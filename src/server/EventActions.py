import logging
import json
from eventmanager import Evt

class EventActions:
    eventActions = []
    effects = {}

    def __init__(self, eventmanager, RHData):
        self._RHData = RHData
        self.Events = eventmanager
        self.logger = logging.getLogger(self.__class__.__name__)

        self.loadActions(None)
        self.Events.on(Evt.ALL, 'Actions', self.doActions)
        self.Events.on(Evt.OPTION_SET, 'Actions', self.loadActions, {}, 200, True)

    def registerEffect(self, handle, handlerFn, args):
        self.effects[handle] = {}
        self.effects[handle]['fn'] = handlerFn
        self.effects[handle]['name'] = args['name']
        self.effects[handle]['fields'] = args['fields']
        return True

    def getRegisteredEffects(self):
        return self.effects

    def loadActions(self, args):
        try:
            self.eventActions = json.loads(self._RHData.get_option('actions'))
        except:
            self.logger.warning("Can't load stored actions JSON")

    def doActions(self, args):
        for action in self.eventActions:
            if action['event'] == args['_eventName']:
                self.effects[action['effect']]['fn'](action, args)