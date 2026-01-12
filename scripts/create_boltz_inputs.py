import copy
import os
from pathlib import Path

import yaml

# Paths
BASE_DIR = "/apps/boltz"
TEMPLATE_FILE = os.path.join(BASE_DIR, "input_template.yaml")
SEQUENCES_FILE = os.path.join(BASE_DIR, "results/sequences.fasta")
LIGANDS_FILE = os.path.join(BASE_DIR, "results/ligands_amp.smi")
MSAS_DIR = os.path.join(BASE_DIR, "results/msas")
PDBS_DIR = os.path.join(BASE_DIR, "pdbs")
OUTPUT_DIR = os.path.join(BASE_DIR, "results/inputs")

# Ensure output directory exists
Path(OUTPUT_DIR).mkdir(exist_ok=True, parents=True)

# Read Input Template
with Path(TEMPLATE_FILE).open() as f:
    base_config = yaml.safe_load(f)

# Parse FASTA
sequences = {}
current_name = None
current_seq = []
with Path(SEQUENCES_FILE).open() as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        if line.startswith(">"):
            if current_name:
                sequences[current_name] = "".join(current_seq)
            current_name = line[1:]
            current_seq = []
        else:
            current_seq.append(line)
    if current_name:
        sequences[current_name] = "".join(current_seq)
print(sequences)

# Parse Ligands
ligands = {}
with Path(LIGANDS_FILE).open() as f:
    for line in f:
        line = line.strip()
        if not line or line.lower().startswith("smiles"):  # Skip header if present
            continue
        parts = line.split()
        if len(parts) >= 2:
            smiles = parts[0]
            name = parts[1]
            ligands[name] = smiles
print(ligands)

# Get Templates
templates = [f for f in os.listdir(PDBS_DIR) if f.endswith(".cif")]
print(templates)

# Generate Inputs
for seq_name, seq_data in sequences.items():
    for lig_name, lig_smiles in ligands.items():
        for template_file in templates:
            config = copy.deepcopy(base_config)

            # Update Sequence
            # Assuming the protein is the first item in 'sequences' list or identifying by id 'A'
            config["sequences"][0]["protein"]["sequence"] = seq_data

            # Update MSA
            # Check if MSA exists
            msa_filename = f"{seq_name.lower()}.a3m"
            msa_path = os.path.join(MSAS_DIR, msa_filename)
            assert Path(msa_path).exists(), f"MSA not found for {seq_name} at {msa_path}"
            config["sequences"][0]["protein"]["msa"] = msa_path

            # Update Ligand
            config["sequences"][1]["ligand"]["smiles"] = lig_smiles

            # Update Template
            # Replacing the existing template block with the new one
            template_path = os.path.join(PDBS_DIR, template_file)
            template_name = os.path.splitext(template_file)[0]

            # We assume the structure of the template block in input_template.yaml is what we want to keep
            # just changing the 'cif' path.
            config["templates"][0]["cif"] = template_path

            # Write Output
            filename = f"{seq_name}_{lig_name}_{template_name}.yaml"
            output_path = os.path.join(OUTPUT_DIR, filename)

            with Path(output_path).open("w") as f:
                yaml.dump(config, f, default_flow_style=False, sort_keys=False)

print(f"Generated input files in {OUTPUT_DIR}")
