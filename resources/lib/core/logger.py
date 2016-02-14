import xbmc
from resources.lib.di.component import Component
from resources.lib.di.requiredfeature import RequiredFeature


class Logger(Component):
    addon = RequiredFeature('addon')

    def __init__(self):
        self.prefix = self.addon.getAddonInfo('id')

    def info(self, text):
        xbmc.log('[%s] %s' % (self.prefix, text), 2)

    def debug(self, text):
        xbmc.log('[%s] %s' % (self.prefix, text), 0)

    def error(self, text):
        xbmc.log('[%s] %s' % (self.prefix, text), 4)
