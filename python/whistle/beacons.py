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

import numpy as np
from smile.frames import Frames


class Beacons(Frames):
    def __init__(self, *args):
        super(Beacons, self).__init__()
        self.column_names["is_echo"] = 15
        self.column_names["origin_node_mac_address"] = 16

    @staticmethod
    def load_csv(file_path):
        converters = Frames._get_default_converters()
        return Beacons(np.loadtxt(file_path, delimiter=',', converters=converters, ndmin=2))