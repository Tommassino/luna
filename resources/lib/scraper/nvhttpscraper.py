import os

from resources.lib.model.apiresponse import ApiResponse
from resources.lib.scraper.abcscraper import AbstractScraper


class NvHTTPScraper(AbstractScraper):
    def __init__(self, plugin, core, nvhttp):
        AbstractScraper.__init__(self, plugin, core)
        self.cover_cache = self._set_up_path(os.path.join(self.base_path, 'art/poster/'))
        self.nvhttp = nvhttp

    def name(self):
        return 'NvHTTP'

    def return_paths(self):
        return [self.cover_cache]

    def is_enabled(self):
        return True

    def get_game_information(self, nvapp):
        game_cover_path = self._set_up_path(os.path.join(self.cover_cache, nvapp.id))
        response = ApiResponse()
        response.name = nvapp.title
        raw_box_art = self.nvhttp.get_box_art(nvapp.id)
        cover_path = self._dump_image_from_data(game_cover_path, nvapp.id, raw_box_art)
        response.posters.append(cover_path)

        return response

    def _dump_image_from_data(self, base_path, id, data):
        file_path = os.path.join(base_path, id + '.png')
        if not os.path.exists(file_path):
            with open(file_path, 'wb') as img:
                img.write(data)
                img.close()

            return file_path
