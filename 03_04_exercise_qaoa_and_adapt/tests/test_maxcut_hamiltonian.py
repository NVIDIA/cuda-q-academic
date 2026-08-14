import unittest

from qaoa_maxcut import maxcut_hamiltonian


class MaxCutHamiltonianTest(unittest.TestCase):
    # Leave this line unchanged. It lets us reuse these tests later.
    implementation = staticmethod(maxcut_hamiltonian)

    def test_nodes_on_the_same_side_have_zero_cost(self):
        # Arrange: choose a graph with one edge of weight 1.
        edges = [(0, 1)]
        edge_weights = [1.0]

        # Act: build its MaxCut Hamiltonian.
        hamiltonian = self.implementation(edges, edge_weights)
        matrix = hamiltonian.to_matrix()

        # Assert: |00> puts both nodes on the same side of the cut.
        self.assertAlmostEqual(matrix[0, 0].real, 0.0)

    def test_cut_edge_has_negative_cost(self):
        # Arrange: choose a graph with one edge of weight 1.
        edges = [(0, 1)]
        edge_weights = [1.0]

        # Act: build its MaxCut Hamiltonian.
        hamiltonian = self.implementation(edges, edge_weights)
        matrix = hamiltonian.to_matrix()

        # Assert: |01> cuts the edge, so its cost is -1.
        self.assertAlmostEqual(matrix[1, 1].real, -1.0)

    # Uncomment this template to add a test.
    # def test_name_the_property_you_are_checking(self):
    #     # Arrange: choose the edges and weights for your test graph.
    #
    #     # Act: build the Hamiltonian and calculate the value to check.
    #
    #     # Assert: compare the actual value with the expected value.


if __name__ == "__main__":
    unittest.main()
