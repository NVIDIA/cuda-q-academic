import numpy as np
from scipy.sparse import csr_matrix
import cudaq_qec as qec
import json
import time

# For fetching data
import requests
import bz2
import os

# Note: running this script will automatically download data if necessary.

### Helper functions ###


def parse_csr_mat(j, dims, mat_name):
    """
    Parse a CSR-style matrix from a JSON file using SciPy's sparse matrix utilities.
    """
    assert len(dims) == 2, "dims must be a tuple of two integers"

    # Extract indptr and indices from the JSON.
    indptr = np.array(j[f"{mat_name}_indptr"], dtype=int)
    indices = np.array(j[f"{mat_name}_indices"], dtype=int)

    # Check that the CSR structure is consistent.
    assert len(indptr) == dims[0] + 1, "indptr length must equal dims[0] + 1"
    assert np.all(
        indices < dims[1]), "All column indices must be less than dims[1]"

    # Create a data array of ones.
    data = np.ones(indptr[-1], dtype=np.uint8)

    # Build the CSR matrix and return it as a dense numpy array.
    csr = csr_matrix((data, indices, indptr), shape=dims, dtype=np.uint8)
    return csr.toarray()


def parse_H_csr(j, dims):
    """
    Parse a CSR-style parity check matrix from an input file in JSON format"
    """
    return parse_csr_mat(j, dims, "H")


def parse_obs_csr(j, dims):
    """
    Parse a CSR-style observable matrix from an input file in JSON format"
    """
    return parse_csr_mat(j, dims, "obs_mat")


### Main decoder loop ###


def run_decoder(filename, num_shots, run_as_batched, print_output=False, osd=0):
    """
    Load a JSON file and decode "num_shots" syndromes.
    """
    t_load_begin = time.time()
    with open(filename, "r") as f:
        j = json.load(f)

    dims = j["shape"]
    assert len(dims) == 2

    # Read the Parity Check Matrix
    H = parse_H_csr(j, dims)
    syndrome_length, block_length = dims
    t_load_end = time.time()

    #print(f"{filename} parsed in {1e3 * (t_load_end-t_load_begin)} ms")

    error_rate_vec = np.array(j["error_rate_vec"])
    assert len(error_rate_vec) == block_length
    obs_mat_dims = j["obs_mat_shape"]
    obs_mat = parse_obs_csr(j, obs_mat_dims)
    assert dims[1] == obs_mat_dims[0]
    file_num_trials = j["num_trials"]
    num_shots = min(num_shots, file_num_trials)
    print(
        f'Your JSON file has {file_num_trials} shots. Running {num_shots} now.')

    # osd_method: 0=Off, 1=OSD-0, 2=Exhaustive, 3=Combination Sweep
    osd_method = osd

    # When osd_method is:
    #  2) there are 2^osd_order additional error mechanisms checked.
    #  3) there are an additional k + osd_order*(osd_order-1)/2 error
    #     mechanisms checked.
    # Ref: https://arxiv.org/pdf/2005.07016
    osd_order = 0

    # Maximum number of BP iterations before attempting OSD (if necessary)
    max_iter = 50

    nv_dec_args = {
        "max_iterations": max_iter,
        "error_rate_vec": error_rate_vec,
        "use_sparsity": True,
        "use_osd": osd_method > 0,
        "osd_order": osd_order,
        "osd_method": osd_method
    }

    if run_as_batched:
        # Perform BP processing for up to 1000 syndromes per batch. If there
        # are more than 1000 syndromes, the decoder will chunk them up and
        # process each batch sequentially under the hood.
        nv_dec_args['bp_batch_size'] = min(1000, num_shots)

    try:
        nv_dec_gpu_and_cpu = qec.get_decoder("nv-qldpc-decoder", H,
                                             **nv_dec_args)
    except Exception as e:
        print(
            'The nv-qldpc-decoder is not available with your current CUDA-Q ' +
            'QEC installation.')
        exit(0)
    decoding_time = 0
    bp_converged_flags = []
    num_logical_errors = 0

    # Batched API
    if run_as_batched:
        syndrome_list = []
        obs_truth_list = []
        for i in range(num_shots):
            syndrome = j["trials"][i]["syndrome_truth"]
            obs_truth = j["trials"][i]["obs_truth"]
            syndrome_list.append(syndrome)
            obs_truth_list.append(obs_truth)
        t0 = time.time()
        results = nv_dec_gpu_and_cpu.decode_batch(syndrome_list)
        t1 = time.time()
        decoding_time += t1 - t0
        for r, obs_truth in zip(results, obs_truth_list):
            bp_converged_flags.append(r.converged)
            dec_result = np.array(r.result, dtype=np.uint8)

            # See if this prediction flipped the observable
            predicted_observable = obs_mat.T @ dec_result % 2
            if print_output == True:
                print(f"predicted_observable: {predicted_observable}")

            # See if the observable was actually flipped according to the truth
            # data
            
            actual_observable = np.array(obs_truth, dtype=np.uint8)
            if print_output == True:
                print(f"actual_observable:    {actual_observable}")

            if np.sum(predicted_observable != actual_observable) > 0:
                num_logical_errors += 1

    # Non-batched API
    else:
        for i in range(num_shots):
            syndrome = j["trials"][i]["syndrome_truth"]
            obs_truth = j["trials"][i]["obs_truth"]

            t0 = time.time()
            bp_converged, dec_result = nv_dec_gpu_and_cpu.decode(syndrome)
            t1 = time.time()
            trial_diff = t1 - t0
            decoding_time += trial_diff

            dec_result = np.array(dec_result, dtype=np.uint8)
            bp_converged_flags.append(bp_converged)

            # See if this prediction flipped the observable
            predicted_observable = obs_mat.T @ dec_result % 2
            if print_output == True:
                print(f"predicted_observable: {predicted_observable}")

            # See if the observable was actually flipped according to the truth
            # data
            actual_observable = np.array(obs_truth, dtype=np.uint8)
            if print_output == True:
                print(f"actual_observable:    {actual_observable}")

            if np.sum(predicted_observable != actual_observable) > 0:
                num_logical_errors += 1

    # Count how many shots the decoder failed to correct the errors
    print(f"{num_logical_errors} logical errors in {num_shots} shots")
    print(
        f"Number of shots that converged with BP processing: {np.sum(np.array(bp_converged_flags))}"
    )
    print(
        f"Average decoding time for {num_shots} shots was {1e3 * decoding_time / num_shots} ms per shot"
    )



