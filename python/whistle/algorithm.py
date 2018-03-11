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
from smile.results import Results
from smile.filter import Filter
import smile.algorithms.tdoa as tdoa
import smile.array as array


def localize_mobile(mobile_node, anchors, all_anchors_beacons, all_mobiles_beacons):
    assert (scc.unit('speed of light in vacuum') == 'm s^-1')
    c = scc.value('speed of light in vacuum')
    c = c * 1e-12  # m/s -> m/ps

    base_anchor = anchors[anchors["base_anchor"] == True, :]
    assert(base_anchor.shape[0] == 1)
    non_base_anchors = anchors[anchors["base_anchor"] == False, :]
    assert(non_base_anchors.shape[0] >= 3)

    mobile_beacons_filter = Filter()
    mobile_beacons_filter.equal("node_mac_address", mobile_node["mac_address"])
    mobile_beacons = mobile_beacons_filter.execute(all_mobiles_beacons)

    anchor_beacons_filter = Filter()
    anchor_beacons_filter.equal("origin_node_mac_address", mobile_node["mac_address"])
    anchors_beacons = anchor_beacons_filter.execute(all_anchors_beacons)

    sequence_numbers, sequence_number_counts = np.unique(mobile_beacons["sequence_number"], return_counts=True)
    results = Results.create_array(sequence_numbers.size, position_dimensions=2)
    results["mac_address"] = mobile_node["mac_address"]

    for j in range(sequence_numbers.size):
        sequence_number = sequence_numbers[j]

        current_mobile_beacons_filter = Filter()
        current_mobile_beacons_filter.equal('sequence_number', sequence_number)
        current_mobile_beacons_filter.equal("direction", hash('RX'))
        current_mobile_beacons = current_mobile_beacons_filter.execute(mobile_beacons)

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

        non_base_echo_rx_beacons = array.sort(non_base_echo_rx_beacons, "node_mac_address")
        non_base_original_rx_beacons = array.sort(non_base_original_rx_beacons, "node_mac_address")

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
            positions.append(tdoa.doan_vesely(coordinates, distances))

        results[j, 'begin_true_position_3d'] = current_mobile_beacons['begin_true_position_3d']
        results[j, 'end_true_position_3d'] = current_mobile_beacons['end_true_position_3d']
        results[j, 'position_2d'] = positions[0]
        pass

    return results
