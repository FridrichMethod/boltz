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


def load_template(template_file: str) -> dict:
    with Path(template_file).open() as f:
        return yaml.safe_load(f)


def parse_fasta(sequences_file: str) -> dict[str, str]:
    sequences = {}
    current_name = None
    current_seq = []
    with Path(sequences_file).open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.startswith(">"):
                if current_name is not None:
                    sequences[current_name] = "".join(current_seq)
                current_name = line[1:]
                current_seq = []
            else:
                current_seq.append(line)
        if current_name is not None:
            sequences[current_name] = "".join(current_seq)
    return sequences


def parse_ligands(ligands_file: str) -> dict[str, str]:
    ligands: dict[str, str] = {}
    with Path(ligands_file).open() as f:
        for line in f:
            line = line.strip()
            if not line or line.lower().startswith("smiles"):  # Skip header if present
                continue
            parts = line.split()
            if len(parts) >= 2:
                smiles = parts[0]
                name = parts[1]
                ligands[name] = smiles
    return ligands


def get_templates(pdbs_dir: str) -> list[str]:
    return [f for f in os.listdir(pdbs_dir) if f.endswith(".cif")]


def generate_inputs(
    sequences: dict[str, str],
    ligands: dict[str, str],
    templates: list[str],
    base_config: dict,
    msas_dir: str,
    pdbs_dir: str,
    output_dir: str,
) -> None:
    Path(output_dir).mkdir(exist_ok=True, parents=True)

    for seq_name, seq_data in sequences.items():
        for lig_name, lig_smiles in ligands.items():
            for template_file in templates:
                config = copy.deepcopy(base_config)

                # Update Sequence
                # Assuming the protein is the first item in 'sequences' list
                config["sequences"][0]["protein"]["sequence"] = seq_data

                # Update MSA
                # Check if MSA exists
                msa_filename = f"{seq_name}.csv"
                msa_path = os.path.join(msas_dir, msa_filename)

                # Check for existence to avoid hard crash if possible, or keep assert if strictness desired
                # Keeping assert as in original logic
                assert Path(msa_path).exists(), f"MSA not found for {seq_name} at {msa_path}"
                config["sequences"][0]["protein"]["msa"] = msa_path

                # Update Ligand
                # Assuming ligand is the second item
                config["sequences"][1]["ligand"]["smiles"] = lig_smiles

                # Update Template
                template_path = os.path.join(pdbs_dir, template_file)
                template_name = os.path.splitext(template_file)[0]

                # We assume the structure of the template block in input_template.yaml is what we want to keep
                # just changing the 'cif' path.
                config["templates"][0]["cif"] = template_path

                # Write Output
                filename = f"{seq_name}_{lig_name}_{template_name}.yaml"
                output_path = os.path.join(output_dir, filename)

                with Path(output_path).open("w") as f:
                    yaml.dump(config, f, default_flow_style=False, sort_keys=False)

    print(f"Generated input files in {output_dir}")


def main() -> None:
    # Allow overriding paths via environment variables or use constants
    # Using constants as defaults

    # Ensure output directory exists
    Path(OUTPUT_DIR).mkdir(exist_ok=True, parents=True)

    base_config = load_template(TEMPLATE_FILE)
    sequences = parse_fasta(SEQUENCES_FILE)
    ligands = parse_ligands(LIGANDS_FILE)
    templates = get_templates(PDBS_DIR)

    generate_inputs(sequences, ligands, templates, base_config, MSAS_DIR, PDBS_DIR, OUTPUT_DIR)


if __name__ == "__main__":
    main()
