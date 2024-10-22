#!/usr/bin/python

# Standard library imports
import logging
import os

from rdkit.Chem.rdmolfiles import *

# OpenBabel imports
try:
    from openbabel import OBConversion, openbabel, vector3
except ImportError as e:
    logging.error(f"Failed to import OpenBabel: {e}")


def MolFromInput(
    molecule,
):  # The code was adapted from https://pypi.org/project/rdkit-utilities/
    """
    Create a RDKit molecule object from an input file of a supported format.

    Raises:
    - SystemExit: If the input file does not exist.
    - TypeError: If the molecule format is not supported or the molecule cannot be created.
    """

    FILE_PARSERS = {
        "mol": MolFromMolFile,
        "mol2": MolFromMol2File,
        "pdb": MolFromPDBFile,
        "sdf": MolFromMolFile,
    }
    # Check if the input is a file
    if not os.path.isfile(molecule):
        raise SystemExit(f"\nERROR! Input file ({molecule}) is not found!!!")

    content_reader = FILE_PARSERS
    mol_format = os.path.splitext(molecule)[1][1:].lower()

    # Attempt to read the file with a specified format
    if mol_format:
        try:
            reader = content_reader[mol_format]
            return reader(molecule)
        except KeyError:
            supported_formats = ", ".join(FILE_PARSERS)
            raise TypeError(
                f"Molecule format {mol_format} not supported. Supported formats: {supported_formats}"
            )

    # Fallback: try reading the file with all supported formats
    for reader in content_reader.values():
        try:
            mol = reader(molecule)
            if mol is not None:
                return mol
        except RuntimeError:
            continue

    # If no reader was successful, raise an error
    supported_formats = ", ".join(FILE_PARSERS)
    raise TypeError(
        f"Could not create an RDKit molecule from {molecule}. Try passing in a `mol_format`. Supported formats: {supported_formats}"
    )


def obabel_convert(
    input_file,
    output_file,
    resname: str = None,
    ph: float = None,
    uniqueNames: bool = False,
):
    """
    Converts molecular file formats using Open Babel, with options for setting residue names,
    adjusting hydrogens for pH, de-aromatizing molecules, and ensuring unique atom names.

    Parameters:
    - input_file: Path to the input file.
    - output_file: Path for the output file.
    - resname: Optional residue name to set for the molecule.
    - ph: Optional pH level to correct hydrogen atoms for specific pH.
    - uniqueNames: If True, ensures that atom names are unique.
    """
    openbabel.obErrorLog.StopLogging()

    conv = openbabel.OBConversion()
    input_format = input_file.split(".")[-1].lower()
    output_format = output_file.split(".")[-1].lower()

    conv.SetInAndOutFormats(input_format, output_format)
    mol = openbabel.OBMol()

    if not conv.ReadFile(mol, input_file):
        raise IOError(f"Failed to read input file: {input_file}")

    if resname is not None:
        for residue in openbabel.OBResidueIter(mol):
            residue.SetName(resname)
        mol.SetTitle(resname)

    if ph is not None:
        mol.AddHydrogens(False, True, ph)

    for bond in openbabel.OBMolBondIter(mol):
        bond.SetAromatic(False)

    for atom in openbabel.OBMolAtomIter(mol):
        atom.SetAromatic(False)

    if not conv.WriteFile(mol, output_file):
        raise IOError(f"Failed to write output file: {output_file}")

    if uniqueNames:
        makeUniqueNames(output_file)
        pass


def makeUniqueNames(mol2_file):
    """
    Ensures that each atom in a MOL2 file has a unique name by appending a number to duplicate atom names.

    Parameters:
    - mol2_file: Path to the MOL2 file to be processed.
    """
    number = {}
    updated_lines = []

    with open(mol2_file, "r") as file:
        lines = file.readlines()

    processing_atoms_section = False
    for line in lines:
        if line.startswith("@<TRIPOS>ATOM"):
            updated_lines.append(line)
            processing_atoms_section = True
        elif line.startswith("@<TRIPOS>") and processing_atoms_section:
            updated_lines.append(line)
            processing_atoms_section = False
        elif processing_atoms_section:
            atom_data = line.split()
            atom_name = atom_data[1]
            if atom_name not in number:
                number[atom_name] = 1
            else:
                number[atom_name] += 1
            atom_data[1] = f"{atom_name}{number[atom_name]}"
            atom_data[7] = "LIG"
            formatted_line = "{0:6d} {1:<8s} {2:10.4f} {3:10.4f} {4:10.4f} {5:<8s} {6:6d} {7:<8s} {8:10.6f}\n".format(
                int(atom_data[0]),
                atom_data[1],
                float(atom_data[2]),
                float(atom_data[3]),
                float(atom_data[4]),
                atom_data[5],
                int(atom_data[6]),
                atom_data[7],
                float(atom_data[8]),
            )
            updated_lines.append(formatted_line)
        else:
            updated_lines.append(line)

    # Rewrite the file with updated lines
    with open(mol2_file, "w") as file:
        file.writelines(updated_lines)


def parse_pdb_line(line):
    """Parse a line of PDB file to extract atom information and coordinates."""
    fields = {
        "record": line[:6].strip(),
        "atom_serial_number": int(line[6:11].strip()),
        "atom_name": line[12:16].strip(),
        "alternate_location_indicator": line[16].strip(),
        "residue_name": line[17:20].strip(),
        "chain_identifier": line[21].strip(),
        "residue_sequence_number": int(line[22:26].strip()),
        "code_for_insertions": line[26].strip(),
        "x": float(line[30:38]),
        "y": float(line[38:46]),
        "z": float(line[46:54]),
        "occupancy": float(line[54:60].strip()),
        "temp_factor": float(line[60:66].strip()),
        "element_symbol": line[76:78].strip(),
        "charge": line[78:80].strip(),
    }
    return fields