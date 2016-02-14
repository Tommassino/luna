import os

import xbmc
import xbmcgui
import routing
import xbmcplugin

from xbmcplugin import addDirectoryItem, endOfDirectory

import resources.lib.config.bootstrap as bootstrapper

from resources.lib.di.requiredfeature import RequiredFeature
from resources.lib.model.game import Game
from resources.lib.views.gameinfo import GameInfo

plugin = bootstrapper.bootstrap()

addon = RequiredFeature('addon').request()

addon_internal_path = addon.getAddonInfo('path')
addon_path = xbmc.translatePath('special://profile/addon_data/%s/.storage/' % addon.getAddonInfo('id'))
if not os.path.isdir(addon_path):
    os.makedirs(addon_path)


@plugin.route('/')
def index():
    default_fanart_path = addon_internal_path + '/fanart.jpg'

    show_games_item = xbmcgui.ListItem(
        label='Games',
        iconImage=addon_internal_path + '/resources/icons/controller.png',
        thumbnailImage=addon_internal_path + '/resources/icons/controller.png'
    )
    show_games_item.setArt({'fanart': default_fanart_path})

    open_settings_item = xbmcgui.ListItem(
        label='Settings',
        iconImage=addon_internal_path + '/resources/icons/cog.png',
        thumbnailImage=addon_internal_path + '/resources/icons/cog.png'
    )
    open_settings_item.setArt({'fanart': default_fanart_path})

    check_update_item = xbmcgui.ListItem(
        label='Check For Update',
        iconImage=addon_internal_path + '/resources/icons/update.png',
        thumbnailImage=addon_internal_path + '/resources/icons/update.png'
    )
    check_update_item.setArt({'fanart': default_fanart_path})

    addDirectoryItem(plugin.handle, plugin.url_for(show_games), show_games_item, True)
    addDirectoryItem(plugin.handle, plugin.url_for(open_settings), open_settings_item)
    addDirectoryItem(plugin.handle, plugin.url_for(check_update), check_update_item)

    endOfDirectory(plugin.handle)


@plugin.route('/settings')
def open_settings():
    addon.openSettings()
    core_monitor = RequiredFeature('core-monitor').request()
    core_monitor.onSettingsChanged()
    del core_monitor


@plugin.route('/update')
def check_update():
    updater = RequiredFeature('update-service').request()
    update = updater.check_for_update(True)
    if update is not None:
        updater.initiate_update(update)


@plugin.route('/actions/create-mapping')
def create_mapping():
    config_controller = RequiredFeature('config-controller').request()
    config_controller.create_controller_mapping()
    del config_controller


@plugin.route('/actions/pair-host')
def pair_host():
    config_controller = RequiredFeature('config-controller').request()
    config_controller.pair_host()
    del config_controller


@plugin.route('/actions/reset-cache')
def reset_cache():
    core = RequiredFeature('core').request()
    confirmed = xbmcgui.Dialog().yesno(
            core.string('name'),
            core.string('reset_cache_warning')
    )

    if confirmed:
        scraper_chain = RequiredFeature('scraper-chain').request()
        scraper_chain.reset_cache()
        del scraper_chain

    del core


@plugin.route('/actions/patch-osmc')
def patch_osmc_skin():
    skinpatcher = RequiredFeature('skin-patcher').request()
    skinpatcher.patch()
    del skinpatcher
    xbmc.executebuiltin('ReloadSkin')


@plugin.route('/actions/rollback-osmc')
def rollback_osmc_skin():
    skinpatcher = RequiredFeature('skin-patcher').request()
    skinpatcher.rollback()
    del skinpatcher
    xbmc.executebuiltin('ReloadSkin')


@plugin.route('/games')
def show_games():
    game_controller = RequiredFeature('game-controller').request()
    xbmcplugin.setContent(plugin.handle, 'movies')
    games = game_controller.get_games_as_list()

    xbmcplugin.addDirectoryItems(plugin.handle, games, len(games))
    xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.endOfDirectory(plugin.handle)


@plugin.route('/games/refresh')
def do_full_refresh():
    game_controller = RequiredFeature('game-controller').request()
    game_controller.get_games()
    del game_controller


@plugin.route('/games/info/<game_id>')
def show_game_info(game_id):
    core = RequiredFeature('core').request()
    game = core.get_storage('game_storage').get(game_id)
    cache_fanart = game.get_selected_fanart()
    cache_poster = game.get_selected_poster()
    window = GameInfo(game, game.name)
    window.doModal()
    del window
    if cache_fanart != game.get_selected_fanart() or cache_poster != game.get_selected_poster():
        xbmc.executebuiltin('Container.Refresh')
    del core
    del game


@plugin.route('/games/launch/<game_id>')
def launch_game(game_id):
    core = RequiredFeature('core').request()
    game_controller = RequiredFeature('game-controller').request()
    core.logger.info('Launching game %s' % game_id)
    game_controller.launch_game(game_id)
    del core
    del game_controller


@plugin.route('/games/launch-from-widget/<xml_id>')
def launch_game_from_widget(xml_id):
    core = RequiredFeature('core').request()
    game_id = int(xml_id)
    internal_game_id = core.get_storage('sorted_game_storage').get(game_id)

    game_controller = RequiredFeature('game-controller').request()
    core.logger.info('Launching game %s' % internal_game_id)
    game_controller.launch_game(internal_game_id)

    del core
    del game_controller

if __name__ == '__main__':
    core = RequiredFeature('core').request()
    updater = RequiredFeature('update-service').request()
    core.check_script_permissions()
    updater.check_for_update()
    del updater

    if addon.getSetting('host'):
        config_helper = RequiredFeature('config-helper').request()
        config_helper.configure()

        game_refresh_required = False

        try:
            if core.get_storage('game_version')['version'] != Game.version:
                game_refresh_required = True
        except KeyError:
            game_refresh_required = True

        if game_refresh_required:
            game_controller = RequiredFeature('game-controller').request()
            # game_controller.get_games()
            del game_controller

        plugin.run()
        del plugin
        del core
    else:
        core = RequiredFeature('core').request()
        xbmcgui.Dialog().ok(
                core.string('name'),
                core.string('configure_first')
        )
        del core
