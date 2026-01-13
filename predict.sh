#!/bin/bash

# This script is used to predict the affinity of a protein-ligand complex using Boltz.

# $1: input file/directory
# $2: output directory

# If $1 is a directory, run batch prediction on all .yaml files in the directory.
# boltz will create a subdirectory in $2 with the name of boltz_results_<input_file_name>.
# so no need to specify the output directory for each input file.

boltz predict "$1" \
    --out_dir "$2" \
    --accelerator gpu \
    --affinity_mw_correction \
    --cache ".cache/boltz" \
    --devices 1 \
    --diffusion_samples 10 \
    --diffusion_samples_affinity 10 \
    --max_msa_seqs 4096 \
    --max_parallel_samples 10 \
    --num_subsampled_msa 1024 \
    --num_workers 4 \
    --output_format pdb \
    --preprocessing-threads "$(nproc)" \
    --recycling_steps 3 \
    --subsample_msa \
    --use_potentials \
    --write_full_pae \
    --write_full_pde
# --override \
# --use_msa_server \
