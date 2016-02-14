import routing

import resources.lib.config.features as provider
import xbmcaddon

from resources.lib.di.featurebroker import features


def bootstrap():
    plugin = routing.Plugin()
    features.provide('plugin', plugin)
    addon = xbmcaddon.Addon()
    features.provide('addon', addon)
    provider.init_di()
    return plugin
