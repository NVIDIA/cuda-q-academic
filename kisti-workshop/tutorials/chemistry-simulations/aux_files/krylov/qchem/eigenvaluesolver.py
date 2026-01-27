import numpy as np
import scipy.linalg as la

def eigen(H, S, *, cond_limit=1e12, eig_tol=1e-10, verbose=False):
    """
    Solve H C = S C E in double precision with automatic stabilisation.

    • Prints κ(S) before and, if projection happens, after stabilisation.
    • Projects out tiny eigenvalues of S when κ(S) is too large.

    Parameters
    ----------
    H, S : (n, n) ndarray (real/complex)
        The Hamiltonian (H) and overlap (S) matrices.
    cond_limit : float
        Trigger value for printing the projection warning.
    eig_tol : float
        Relative cut-off (s_val < eig_tol * s_val_max are removed).
    verbose : bool
        Print diagnostics.
    """
    H = np.asarray(H, dtype=np.complex128)
    S = np.asarray(S, dtype=np.complex128)

    # 1. Diagonalise S (assumed Hermitian)
    s_vals, U = la.eigh(S)
    # Drop negative round-off noise by clipping to zero
    s_vals = np.clip(s_vals, 0.0, None)

    pos = s_vals[s_vals > 0]
    if pos.size == 0:
        raise np.linalg.LinAlgError("S is numerically singular: no positive eigenvalues.")

    kappa0 = pos.max() / pos.min()
    if verbose:
        print(f"κ(S) before projection : {kappa0:.3e}")

    # 2. Decide which eigenvalues to keep
    s_max = pos.max()
    # Define an absolute cutoff based on machine precision and the relative tolerance
    abs_cut = max(np.finfo(s_vals.dtype).eps, eig_tol * s_max)

    keep = s_vals > abs_cut
    
    # Check if we discarded everything
    if not np.any(keep):
        raise np.linalg.LinAlgError(f"All eigenvalues discarded; S is singular (cutoff={abs_cut:.2e}).")

    # Conditionally print the projection message if the condition number was the trigger
    if verbose and kappa0 > cond_limit:
        n_removed = S.shape[0] - np.sum(keep)
        if n_removed > 0:
            print(f"  projecting out {n_removed} eigenvalue(s) < {abs_cut:.3e}")
    
    lam_keep = s_vals[keep]  # Now guaranteed to be strictly positive
    U_keep = U[:, keep]

    # 3. Build the transformation matrix X = U_keep @ diag(1/sqrt(lam_keep))
    # Broadcasting correctly scales each column of U_keep
    X = U_keep / np.sqrt(lam_keep)

    # 4. Solve the reduced (and well-conditioned) standard eigenvalue problem
    H_prime = (X.conj().T @ H) @ X
    e_prime, C_prime = la.eigh(H_prime) # Use eigh since H_prime is Hermitian

    # 5. Back-transform eigenvectors to the original basis
    C = X @ C_prime

    # 6. Report improved condition number if projection happened
    if verbose and kappa0 > cond_limit:
        kappa1 = lam_keep.max() / lam_keep.min()
        print(f"κ(S) after  projection : {kappa1:.3e}")

    return e_prime, C