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

import os.path

import numpy as np

import smile.simulation
from smile.nodes import Nodes
from smile.results import Results
from whistle.anchors import Anchors
from whistle.beacons import Beacons
from whistle.algorithm import localize_mobile


class Simulation(smile.simulation.Simulation):
    def run_offline(self, directory_path):
        anchors = Anchors.load_csv(os.path.join(directory_path, 'whistle_anchors.csv'))
        mobiles = Nodes.load_csv(os.path.join(directory_path, 'whistle_mobiles.csv'))
        mobile_beacons = Beacons.load_csv(os.path.join(directory_path, 'whistle_mobile_beacons.csv'))
        anchor_beacons = Beacons.load_csv(os.path.join(directory_path, 'whistle_anchor_beacons.csv'))

        results = None
        for mobile_node in mobiles:
            mobile_results = localize_mobile(mobile_node, anchors, anchor_beacons, mobile_beacons)
            if results is None:
                results = mobile_results
            else:
                results = Results(np.concatenate((results, mobile_results), axis=0))

        return results
