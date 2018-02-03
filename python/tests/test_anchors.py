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

# There's no need to display interactive plots
import matplotlib
matplotlib.use('AGG')

import unittest
from io import StringIO
import numpy as np
from whistle.anchors import Anchors


class TestAnchors(unittest.TestCase):
    def test_load_csv(self):
        content = StringIO("17592186044417,0.000000,0.000000,0.000000,1,0\n17592186044418,75.000000,0.000000,0.000000,0,35000000000")

        # Check whether data is loaded into correct array
        nodes = Anchors.load_csv(content)
        self.assertTrue(isinstance(nodes, np.ndarray))
        self.assertTupleEqual((2, 6), nodes.shape)

        # Check access to whistle-specific fields
        np.testing.assert_equal((1, 0), nodes[:, Anchors.BASE_ANCHOR])
        np.testing.assert_equal((0, 35000000000), nodes[:, Anchors.ECHO_DELAY])


if __name__ == '__main__':
    unittest.main()
