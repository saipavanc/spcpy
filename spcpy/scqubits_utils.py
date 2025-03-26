# scqubits_utils.py
# Contains utility functions for the scqubits package.

import numpy as np
from typing import Dict, Optional, Tuple, Union, List
import qutip as qt
import matplotlib.pyplot as plt
import matplotlib.animation as anim
import scqubits as scq
import scqubits.core.oscillator as osc
from scqubits.core.qubit_base import QubitBaseClass


class scq_plot:

    def __init__(
        self,
        qubit: QubitBaseClass,
        evals_count: Optional[int] = None,
        generate_esys: bool = False,
    ):
        """
        Class to help plot certain properties of a qubit.

        Args:
            qubit (scq.QubitBaseClass): The qubit object.
            evals_count (int, optional): Number of eigenvalues to compute. Defaults to 6.
        """
        self.qubit = qubit
        self.is_circuit = isinstance(qubit, scq.Circuit)
        if generate_esys:
            if self.is_circuit:
                self.esys = qubit.generate_bare_eigensys()
            else:
                self.esys = qubit.eigensys(evals_count=evals_count)

    def update(self):
        """
        Update the eigenvalues of the qubit.
        """
        self.esys = self.qubit.eigensys(eval_count=50)

    def transformation_mat_ho_to_disc_phi(
        self,
        phi_grid: Optional[scq.Grid1d] = None,
        osc_length: Optional[float] = None,
        var_index: Optional[int] = None,
    ) -> np.ndarray:
        """
        Generates the transformation matrix from harmonic oscillator basis to phi basis.

        Args:
            phi_grid (scq.Grid1d): grid for phi basis.
            osc_length (Optional[float]): Osc length for ho basis. Defaults to None.
            var_index (Optional[int], optional): Var index for the Circuit module. Defaults to None.

        Raises:
            ValueError: The var_index should be provided and osc_lenght should be None for a Circuit module.
            ValueError: phi_grid and osc_length should be provided for an extended variable for a scqubits non-Circuit qubit.
            ValueError: If variable corresponding to var_index is harmonic, then osc_length should be None.

        Returns:
            np.ndarray: Transformation matrix from harmonic oscillator basis to phi basis.
        """
        if self.is_circuit and (var_index is None or osc_length is not None):
            raise ValueError(
                "The var_index should be provided and osc_lenght should be None for a Circuit module."
            )
        if not self.is_circuit and (var_index is not None):
            if phi_grid is None or osc_length is None:
                raise ValueError(
                    "phi_grid and osc_length should be provided for an extended variable for a scqubits non-Circuit qubit."
                )
        if self.is_circuit:
            if (
                self.qubit._basis_for_var_index(var_index) == "harmonic"
                and osc_length is not None
            ):
                raise ValueError(
                    "If variable corresponding to var_index is harmonic, then osc_length should be None."
                )

        dim = self.qubit.hilbertdim()
        if self.is_circuit:
            phi_grid = phi_grid or self.qubit.osc_lengths[var_index]
            osc_length = self.qubit.osc_lengths[var_index]
        phi_basis_labels = phi_grid.make_linspace()
        T = np.zeros((dim, len(phi_basis_labels)), dtype=complex)

        for n in range(dim):
            T[:, n] = osc.harm_osc_wavefunction(n, phi_basis_labels, osc_length)
        return T

    def projection_ops_phi(
        self,
        sift_size: int,
        phi_grid: Optional[scq.Grid1d] = None,
        osc_length: Optional[float] = None,
        var_index: Optional[int] = None,
        var_basis_type: Optional[str] = None,
        esys=None,
    ) -> List[qt.Qobj]:
        """
        Returns the eops for the qubit in the phi basis.
        The sift_size is used to break the phi range into bins of size sift_size.
        The projection operator for each bin is returned.
        """

        if not self.is_circuit and var_basis_type is None:
            raise ValueError(
                "var_basis_type should be provided for a non-Circuit qubit."
            )
        if self.is_circuit and var_basis_type is not None:
            raise ValueError(
                "var_basis_type should not be provided for a Circuit module."
            )
        if self.is_circuit:
            var_basis_type = self.qubit._basis_for_var_index(var_index)

        if var_basis_type == "harmonic":
            T = self.transformation_mat_ho_to_disc_phi(phi_grid, osc_length, var_index)

        if self.is_circuit and var_index not in self.qubit.var_categories["extended"]:
            raise ValueError(
                "The variable corresponsing to the var_index should be extended."
            )

        if self.is_circuit:
            phi_grid = phi_grid or scq.Grid1d(
                *self.qubit.discretized_phi_range[var_index], self.qubit.cutoff_ext_1
            )
        p_ops = []  # return list of projection operators
        esys = esys or self.esys
        if self.is_circuit:
            sift_size = 2
            θ1_coarse = phi_grid.make_linspace()[::sift_size]

            for idx, pos in enumerate(θ1_coarse):
                child = self.qubit.return_root_child(var_index)
                disc_phi_proj = np.zeros(phi_grid.pt_count)
                for j in range(
                    idx * sift_size - int(sift_size / 2),
                    idx * sift_size + int(sift_size / 2),
                ):
                    disc_phi_proj[j] = 1
                disc_phi_proj = qt.Qobj(np.diag(disc_phi_proj))
                if var_basis_type == "harmonic":
                    disc_phi_proj = T.dag() * disc_phi_proj * T
                # use kron_operator for full subsys
                disc_phi_proj = child._kron_operator(disc_phi_proj, var_index)
                # convert to HD basis if necessary
                p_op = self.qubit.identity_wrap_for_hd(
                    disc_phi_proj, child, bare_esys=esys
                )
                # convert to eigenbasis and add to eops
                p_ops.append(p_op)
        return p_ops, θ1_coarse
    
    
def bare_idx_to_raveled_idx(
    bare_indices: Union[tuple, list], circuit: QubitBaseClass
) -> int:
    """
    Convert bare index to raveled index.

    Args:
        bare_index (tuple, list): List of bare indices for all the subsystems
        circuit (QubitBaseClass): Circuit Class or HilbertSpace object.

    Returns:
        int: The raveled index.
    """
    if sum(((np.array(bare_indices)+1) - np.array(circuit.subsystem_trunc_dims)) > 0) > 0:
        raise ValueError("Bare indices are out of bounds, check the subsystem truncation dimensions")
    raveled_index = 0
    for idx, dim in enumerate(circuit.subsystem_trunc_dims):
        raveled_index += bare_indices[idx] * int(np.prod(circuit.subsystem_trunc_dims[idx+1:]))
    return raveled_index