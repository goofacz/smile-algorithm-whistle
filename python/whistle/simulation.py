#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see http:#www.gnu.org/licenses/.
#

from os import path
from whistle.anchors import Anchors
from smile.frames import Frames
from smile.helpers import mac_address_to_string


def load_nodes(directory_path):
    anchors_file_path = path.join(directory_path, 'whistle_anchors.csv')
    mobiles_file_path = path.join(directory_path, 'whistle_mobiles.csv')
    return Anchors.load_csv(anchors_file_path), Anchors.load_csv(mobiles_file_path)


def load_nodes_beacons(directory_path, mac_addresses):
    beacons = {}
    for mac_address in mac_addresses:
        file_path = path.join(directory_path, 'whistle_anchor_{0}.csv'.format(mac_address_to_string(mac_address)))
        beacons[mac_address] = Frames.load_csv(file_path)
    return beacons


def load_mobile_beacons(directory_path, mac_address):
    mac_address = mac_address_to_string(mac_address)
    file_path = path.join(directory_path, 'whistle_mobile_{0}.csv'.format(mac_address))
    return Frames.load_csv(file_path)
