import sys
import unittest
from pathlib import Path

import cudaq
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import qaoa_maxcut
import qaoa_maxcut_solvers


class QaoaMaxCutTest(unittest.TestCase):
    def test_zero_parameters_return_equal_superposition(self):
        cudaq.set_target("qpp-cpu")
        zero_parameters = [0.0, 0.0]

        state = cudaq.get_state(
            qaoa_maxcut.qaoa,
            qaoa_maxcut.NUM_QUBITS,
            qaoa_maxcut.LAYER_COUNT,
            qaoa_maxcut.EDGE_SOURCES,
            qaoa_maxcut.EDGE_TARGETS,
            qaoa_maxcut.EDGE_WEIGHTS,
            zero_parameters,
        )
        expected = np.ones(2**qaoa_maxcut.NUM_QUBITS) / np.sqrt(
            2**qaoa_maxcut.NUM_QUBITS
        )

        np.testing.assert_allclose(np.array(state), expected, atol=1e-7)

    def test_custom_qaoa_matches_cudaq_solvers(self):
        cudaq.set_target("qpp-cpu")

        custom_energy, _ = qaoa_maxcut.solve_qaoa()
        solvers_result = qaoa_maxcut_solvers.solve_qaoa()

        self.assertAlmostEqual(
            custom_energy, solvers_result.optimal_value, delta=1e-4
        )

    def test_optimized_parameters_match(self):
        cudaq.set_target("qpp-cpu")

        _, custom_parameters = qaoa_maxcut.solve_qaoa()
        solvers_result = qaoa_maxcut_solvers.solve_qaoa()

        np.testing.assert_allclose(
            custom_parameters,
            solvers_result.optimal_parameters,
            atol=1e-7,
        )


if __name__ == "__main__":
    unittest.main()
