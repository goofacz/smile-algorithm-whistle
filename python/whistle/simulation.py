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
from whistle.beacons import Beacons
from smile.nodes import Nodes


def load_nodes(directory_path):
    anchors_file_path = path.join(directory_path, 'whistle_anchors.csv')
    mobiles_file_path = path.join(directory_path, 'whistle_mobiles.csv')
    return Anchors.load_csv(anchors_file_path), Nodes.load_csv(mobiles_file_path)


def load_mobiles_beacons(directory_path):
    file_path = path.join(directory_path, 'whistle_mobiles_beacons.csv')
    return Beacons.load_csv(file_path)


def load_anchors_beacons(directory_path):
    file_path = path.join(directory_path, 'whistle_anchors_beacons.csv')
    return Beacons.load_csv(file_path)
