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

from itertools import combinations
from whistle.beacons import Beacons
from whistle.anchors import Anchors
from smile.results import Results
from smile.filter import Filter
import smile.algorithms as algorithms


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

    base_anchor = anchors[anchors["base_anchor"] == True, :]
    assert(base_anchor.shape[0] == 1)
    non_base_anchors = anchors[anchors["base_anchor"] == False, :]
    assert(non_base_anchors.shape[0] >= 3)

    mobile_beacons = all_mobiles_beacons[all_mobiles_beacons["node_mac_address"] == mac_address, :]
    anchors_beacons = all_anchors_beacons[all_anchors_beacons["origin_node_mac_address"] == mac_address, :]

    sequence_numbers, sequence_number_counts = np.unique(mobile_beacons["sequence_number"], return_counts=True)
    results = Results.create_array(sequence_numbers.size, position_dimensions=2)

    for sequence_number in sequence_numbers:
        sequence_number_condition = anchors_beacons["sequence_number"] == sequence_number
        current_anchors_beacons = anchors_beacons[sequence_number_condition, :]

        beacons_filter = Filter()
        beacons_filter.equal("node_mac_address", base_anchor[0, "mac_address"])
        beacons_filter.equal("is_echo", 0)
        beacons_filter.equal("direction", hash('RX'))
        base_original_rx_beacons = beacons_filter.execute(current_anchors_beacons)

        beacons_filter = Filter()
        beacons_filter.equal("node_mac_address", base_anchor[0, "mac_address"])
        beacons_filter.equal("is_echo", 1)
        beacons_filter.equal("direction", hash('TX'))
        base_echo_tx_beacons = beacons_filter.execute(current_anchors_beacons)

        beacons_filter = Filter()
        beacons_filter.not_equal("node_mac_address", base_anchor[0, "mac_address"])
        beacons_filter.equal("is_echo", 0)
        beacons_filter.equal("direction", hash('RX'))
        non_base_original_rx_beacons = beacons_filter.execute(current_anchors_beacons)

        beacons_filter = Filter()
        beacons_filter.not_equal("node_mac_address", base_anchor[0, "mac_address"])
        beacons_filter.equal("is_echo", 1)
        beacons_filter.equal("direction", hash('RX'))
        non_base_echo_rx_beacons = beacons_filter.execute(current_anchors_beacons)

        non_base_echo_rx_beacons = algorithms.sort(non_base_echo_rx_beacons, "node_mac_address")
        non_base_original_rx_beacons = algorithms.sort(non_base_original_rx_beacons, "node_mac_address")

        positions = []
        for non_base_anchors_indices in combinations((0, 1, 2), 2):
            tD2S = []
            coordinates = [np.array(base_anchor[0, "position_2d"])]

            for i in non_base_anchors_indices:
                distance = np.abs(np.linalg.norm(base_anchor[0, "position_2d"] - non_base_anchors[i, "position_2d"]))
                tA2S = base_echo_tx_beacons[0, "begin_clock_timestamp"] - base_original_rx_beacons[0, "begin_clock_timestamp"]
                tB2S = non_base_echo_rx_beacons[i, "begin_clock_timestamp"] - non_base_original_rx_beacons[i, "begin_clock_timestamp"]
                tD2S = np.append(tD2S, distance / c - (tB2S - tA2S))

                coordinates.append(non_base_echo_rx_beacons[i, "begin_true_position_2d"])

            distances = np.array((float('nan'), tD2S[0], tD2S[1])) * c
            coordinates = np.array(coordinates)
            positions.append(_tdoa_analytical(coordinates, distances))

            pass

    # TODO Fill results
    return results
