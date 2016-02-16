import os
import stat

from xbmcswift2 import TimedStorage

import xbmc

from datetime import timedelta
from xml.etree.ElementTree import ElementTree

from resources.lib.di.component import Component
from resources.lib.di.requiredfeature import RequiredFeature

STRINGS = {
    'name':                30000,
    'addon_settings':      30100,
    'full_refresh':        30101,
    'choose_ctrl_type':    30200,
    'enter_filename':      30201,
    'starting_mapping':    30202,
    'mapping_success':     30203,
    'set_mapping_active':  30204,
    'mapping_failure':     30205,
    'pair_failure_paired': 30206,
    'configure_first':     30207,
    'reset_cache_warning': 30208
}


class Core(Component):
    plugin = RequiredFeature('plugin')
    addon = RequiredFeature('addon')
    logger = RequiredFeature('logger')

    def __init__(self):
        self.logger.info('[CoreService] - initialized')
        self.internal_path = self.addon.getAddonInfo('path')
        self._addon_id = self.addon.getAddonInfo('id')

        self._storage_path = xbmc.translatePath(
            'special://profile/addon_data/%s/.storage/' % self._addon_id)
        if not os.path.isdir(self._storage_path):
            os.makedirs(self._storage_path)

    def string(self, string_id):
        if string_id in STRINGS:
            return self.addon.getLocalizedString(STRINGS[string_id]).encode('utf-8')
        else:
            return string_id

    def check_script_permissions(self):
        st = os.stat(self.internal_path + '/resources/lib/launchscripts/osmc/launch.sh')
        if not bool(st.st_mode & stat.S_IXUSR):
            os.chmod(self.internal_path + '/resources/lib/launchscripts/osmc/launch.sh', st.st_mode | 0111)
            self.logger.info('Changed file permissions for launch')

        st = os.stat(self.internal_path + '/resources/lib/launchscripts/osmc/launch-helper-osmc.sh')
        if not bool(st.st_mode & stat.S_IXUSR):
            os.chmod(self.internal_path + '/resources/lib/launchscripts/osmc/launch-helper-osmc.sh', st.st_mode | 0111)
            self.logger.info('Changed file permissions for launch-helper-osmc')

        st = os.stat(self.internal_path + '/resources/lib/launchscripts/osmc/moonlight-heartbeat.sh')
        if not bool(st.st_mode & stat.S_IXUSR):
            os.chmod(self.internal_path + '/resources/lib/launchscripts/osmc/moonlight-heartbeat.sh', st.st_mode | 0111)
            self.logger.info('Changed file permissions for moonlight-heartbeat')

    def get_storage(self, storage_name, TTL=None):
        if not hasattr(self, '_unsynced_storages'):
            self._unsynced_storages = {}
        filename = os.path.join(self._storage_path, storage_name)
        try:
            storage = self._unsynced_storages[filename]
        except KeyError:
            if TTL:
                TTL = timedelta(minutes=TTL)
            try:
                storage = TimedStorage(filename=filename, TTL=TTL)
            except ValueError:
                os.remove(filename)
                storage = TimedStorage(filename=filename, TTL=TTL)

            self._unsynced_storages[filename] = storage
        return storage

    def get_storage_path(self):
        return self._storage_path

    def get_active_skin(self):
        userdata_folder = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(self._storage_path))))
        guisettings_file = os.path.join(userdata_folder, 'guisettings.xml')
        xml_root = ElementTree(file=guisettings_file).getroot()
        active_skin = xml_root.find('lookandfeel').find('skin').text
        return active_skin
