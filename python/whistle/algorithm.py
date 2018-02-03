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
import scipy.constants as scc

from whistle.beacons import Beacons
from smile.results import Results


# Algorithm based on:
# S. Van Doan and J. Vesely, "The effectivity comparison of TDOA analytical solution methods,"
# 2015 16th International Radar Symposium (IRS), Dresden, 2015, pp. 800-805.
def _tdoa_analytical(coordinates, distances):
    """
    S. Van Doan and J. Vesely, "The effectivity comparison of TDOA analytical solution methods,"
    2015 16th International Radar Symposium (IRS), Dresden, 2015, pp. 800-805.
    """
    L = distances[1]
    R = distances[2]
    Xl = coordinates[1, 0] - coordinates[0, 0]
    Yl = coordinates[1, 1] - coordinates[0, 1]
    Xr = coordinates[2, 0] - coordinates[0, 0]
    Yr = coordinates[2, 1] - coordinates[0, 1]

    A = -2 * np.asanyarray(((Xl, Yl),
                            (Xr, Yr)))

    B = np.asanyarray(((-2 * L, L ** 2 - Xl ** 2 - Yl ** 2),
                       (2 * R, R ** 2 - Xr ** 2 - Yr ** 2)))

    tmp, _, _, _ = np.linalg.lstsq(A, B, rcond=None)
    a = tmp[0, 0] ** 2 + tmp[1, 0] ** 2 - 1
    b = 2 * (tmp[0, 0] * tmp[0, 1] + tmp[1, 0] * tmp[1, 1])
    c = tmp[0, 1] ** 2 + tmp[1, 1] ** 2

    K = np.max(np.real(np.roots((a, b, c))))

    X = tmp[0, 0] * K + tmp[0, 1] + coordinates[0, 0]
    Y = tmp[1, 0] * K + tmp[1, 1] + coordinates[0, 1]

    return np.asarray((X, Y))


def localize_mobile(mac_address, anchors, all_anchors_beacons, all_mobiles_beacons):
    assert (scc.unit('speed of light in vacuum') == 'm s^-1')
    c = scc.value('speed of light in vacuum')
    c = c * 1e-12  # m/s -> m/ps

    # Filter out other mobile nodes
    mobile_beacons = all_mobiles_beacons[all_mobiles_beacons[:, Beacons.NODE_MAC_ADDRESS] == mac_address]

    # Filter out all sequence numbers for which mobile node received less than three beacons
    sequence_numbers, sequence_number_counts = np.unique(mobile_beacons[:, Beacons.SEQUENCE_NUMBER], return_counts=True)
    # sequence_numbers = sequence_numbers[sequence_number_counts >= 3]

    results = Results.create_array(sequence_numbers.size, position_dimensions=2)

    for sequence_number in sequence_numbers:
        sequence_number_condition = mobile_beacons[:, Beacons.SEQUENCE_NUMBER] == sequence_number
        is_echo_condition = mobile_beacons[:, Beacons.IS_ECHO] == 1
        is_not_echo_condition = np.logical_not(is_echo_condition)

        original_beacons_condition = np.logical_and(sequence_number_condition, is_not_echo_condition)
        echo_beacons_condition = np.logical_and(sequence_number_condition, is_echo_condition)

        original_beacons = mobile_beacons[original_beacons_condition, :]
        echo_beacons = mobile_beacons[echo_beacons_condition, :]

    return results
