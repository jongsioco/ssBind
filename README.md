# ssBind: Sub-Structure-based alternative BINDing modes generator for protein-ligand systems


ssBind offers different methods for generating multiple conformations by restraining certain sub-structures. This feature enables researchers to systematically explore the effects of various substituents attached to a common scaffold on the binding and to refine the interaction patterns between ligand molecules and their protein targets.

## Available methods for conformer generation

* Random conformer generation with RDKit 
* Dihedral angle sampling
* PLANTS docking tool
* rDock docking tool
* Scoring and minimization with AutoDock Vina or smina
* Overall minimization using gromacs with GAFF, CGenFF and OpenFF

## Installation (from source)
You'll get the develop branch, which may be ahead of the latest release.
```bash
$ git clone https://github.com/suleymanselim/ssBind
$ cd ssBind
$ pip install .
```

## Examples using the command line scripts

#### 1. Random conformational sampling using RDKit
```console
run_ssBind.py --reference reference.mol2 --ligand ligand.mol2 --receptor receptor.pdb --generator rdkit 
```
#### 2. Using dihedral angles to generate conformers
```console
run_ssBind.py --reference reference.mol2 --ligand ligand.mol2 --receptor receptor.pdb --generator angle 
```
#### 3. Generating conformers using PLANTS docking tool
PLANTS allows to restrain the position of a ring system or a single non-ring atom in docking. In this case, all translational and rotational degrees of freedom of the fixed scaffold are completely neglected. The code automatically determines the ring system to be fixed in the reference scaffold.

```console
run_ssBind.py --reference reference.mol2 --ligand ligand.mol2 --receptor receptor.pdb --generator plants 

```
Some side-chains can also be treated flexibly with PLANTS.
```console
## A subset of the sidechains around the ligand within 5 Å in the binding pocket will be allowed to move.
run_ssBind.py --reference reference.mol2 --ligand ligand.mol2 --receptor receptor.pdb --generator plants --flexDist 5

## You can also determine the flexible sidechains
run_ssBind.py --reference reference.mol2 --ligand ligand.mol2 --receptor receptor.pdb --generator plants --flexList "MET49,MET165"

```
#### 4. Tethered scaffold docking with rDock
```console
run_ssBind.py --reference reference.mol2 --ligand ligand.mol2 --receptor receptor.pdb --generator rdock 
```
## Python tutorial

#### 1. Generating conformers using PLANTS

```python
from ssBind import SSBIND
from ssBind.chem_tools import MolFromInput

## Input files
reference_substructure = MolFromInput('reference.mol2')
query_molecule = MolFromInput('ligand.mol2')
receptor_file = 'receptor.pdb'

ssbind = SSBIND(reference_substructure = reference_substructure, query_molecule =query_molecule, receptor_file = receptor_file)

## PLANTS generates many conformers 'conformers.sdf' and their scores 'Scores.csv'
ssbind.generate_conformers_plants()

## Clustering identifies some binding modes based on binding scores and PCA.
ssbind.clustering(conformers = 'conformers.sdf', scores = 'Scores.csv')
```


