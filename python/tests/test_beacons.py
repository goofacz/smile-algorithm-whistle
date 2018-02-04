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

import unittest
from io import StringIO
import numpy as np
from whistle.beacons import Beacons


class TestBeacons(unittest.TestCase):
    def test_load_csv(self):
        content = StringIO(
            "12345678,RX,105000927418,205000927418,37.500000,87.500000,79.000000,305010927418,405010927418,137.500000,127.500000,46.000000,17592186044420,281474976710655,1,0,0\n"
            "98765432,TX,140001177591,140001177591,37.500000,37.500000,0.000000,140011177591,140011177591,37.500000,37.500000,0.000000,17592186044417,281474976710655,2,1,1122334455")

        # Check access to new fields
        nodes = Beacons.load_csv(content)
        self.assertTupleEqual((2, 17), nodes.shape)

        np.testing.assert_equal((0, 1), nodes[:, Beacons.IS_ECHO])
        np.testing.assert_equal((0, 1122334455), nodes[:, Beacons.ORIGIN_NODE_MAC_ADDRESS])


if __name__ == '__main__':
    unittest.main()
