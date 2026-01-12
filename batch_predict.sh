#!/bin/bash

# This script is used to batch predict the affinity of a protein-ligand complex using Boltz.

for input in "$1"/*.yaml; do
    echo "--------------------------------"
    echo "Input: $input"
    output="$2/$(basename "$input" .yaml)"
    echo "Output: $output"
    ./predict.sh "$input" "$output"
done
