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

import argparse
from simulation import *
from whistle.anchors import Anchors

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process Whistle ranging data.')
    parser.add_argument('logs_directory_path', type=str, nargs=1, help='Path to directory holding CSV logs')
    arguments = parser.parse_args()
    logs_directory_path = arguments.logs_directory_path[0]

    anchors, mobiles = load_nodes(logs_directory_path)
    anchors_beacons = load_nodes_beacons(logs_directory_path, anchors[:, Anchors.MAC_ADDRESS])
    simulation_results = None
    for mobile_address in mobiles[:, Anchors.MAC_ADDRESS]:
        beacons = load_mobile_beacons(logs_directory_path, mobile_address)