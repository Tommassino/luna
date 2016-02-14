import xbmcgui

from resources.lib.di.requiredfeature import RequiredFeature
from resources.lib.model.game import Game


class GameController:
    plugin = RequiredFeature('plugin')
    core = RequiredFeature('core')
    moonlight_helper = RequiredFeature('moonlight-helper')
    scraper_chain = RequiredFeature('scraper-chain')
    logger = RequiredFeature('logger')

    def __init__(self):
        pass

    def get_games(self):
        """
        Fills local game storage with scraper results (if enabled) or game names (if scrapers are disabled)
        """
        game_list = self.moonlight_helper.list_games()

        progress_dialog = xbmcgui.DialogProgress()
        progress_dialog.create(
            self.core.string('name'),
            'Refreshing Game List'
        )

        bar_movement = int(1.0 / len(game_list) * 100)

        storage = self.core.get_storage('game_storage')
        cache = storage.raw_dict().copy()
        storage.clear()

        i = 1
        for game_name in game_list:
            progress_dialog.update(bar_movement * i, 'Processing: %s' % game_name, '')
            if self.plugin.get_setting('disable_scraper', bool):
                self.logger.info('Scraper have been disabled, just adding game names to list.')
                progress_dialog.update(bar_movement * i,
                                       line2='Scrapers have been disabled, just adding game names to list.')
                storage[game_name] = Game(game_name, None)
            else:
                if game_name in cache:
                    if not storage.get(game_name):
                        progress_dialog.update(bar_movement * i, line2='Restoring information from cache')
                        storage[game_name] = cache.get(game_name)[0]
                else:
                    try:
                        progress_dialog.update(bar_movement * i, line2='Getting Information from Online Sources')
                        storage[game_name] = self.scraper_chain.query_game_information(game_name)
                    except KeyError:
                        self.logger.info(
                                'Key Error thrown while getting information for game {0}: {1}'
                                .format(game_name,
                                        KeyError.message))
                        storage[game_name] = Game(game_name, None)
            i += 1

        game_version_storage = self.core.get_storage('game_version')
        game_version_storage.clear()
        game_version_storage['version'] = Game.version

        storage.sync()
        game_version_storage.sync()

    def get_games_as_list(self):
        """
        Parses contents of local game storage into a list that can be interpreted by Kodi
        :rtype: list
        """

        def context_menu(game_id):
            return [
                (
                    'Game Information',
                    'XBMC.RunPlugin(%s)' % self.plugin.url_for_path('/games/info/%s' % game_id)
                ),
                (
                    self.core.string('addon_settings'),
                    'XBMC.RunPlugin(%s)' % self.plugin.url_for_path('/settings')
                ),
                (
                    self.core.string('full_refresh'),
                    'XBMC.RunPlugin(%s)' % self.plugin.url_for_path('/games/refresh')
                )
            ]

        storage = self.core.get_storage('game_storage')

        if len(storage.raw_dict()) == 0:
            self.get_games()

        items = []
        for i, game_name in enumerate(storage):
            # TODO: Find a way to implement storage ...
            game = storage.get(game_name)

            path = self.plugin.url_for_path('/games/launch/%s' % game.name)

            game_item = xbmcgui.ListItem(
                label=game.name,
                iconImage=game.get_selected_poster(),
                thumbnailImage=game.get_selected_poster(),
                path=path
            )

            game_item.setInfo('video', {
                    'year': game.year,
                    'plot': game.plot,
                    'genre': game.get_genre_as_string(),
                    'originaltitle': game.name,
                })

            game_item.setArt({'fanart': game.get_selected_fanart().get_original()})
            game_item.addContextMenuItems(context_menu(game_name), True)

            items.append((path, game_item, True))

        return items

    def launch_game(self, game_name):
        """
        Launches game with specified name
        :type game_name: str
        """
        self.moonlight_helper.launch_game(game_name)
