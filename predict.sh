#!/bin/bash

# This script is used to predict the affinity of a protein-ligand complex using Boltz.

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
    --override \
    --recycling_steps 3 \
    --subsample_msa \
    --use_potentials \
    --write_full_pae \
    --write_full_pde
    # --use_msa_server \
