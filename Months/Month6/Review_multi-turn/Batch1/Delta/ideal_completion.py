def pymatgen_code():
    from pymatgen.core import Lattice, Structure
    from pymatgen.io.cif import CifWriter

    # Define lattice parameters
    a = 11.14  # Angstroms
    lattice = Lattice.cubic(a)

    # Define atomic positions
    species = ["Bi", "Bi", "O"]
    coords = [
        [0.25, 0.25, 0.25],       # Bi(1) at 8b
        [0.4703, 0.0, 0.25],      # Bi(2) at 24d
        [0.3936, 0.1545, 0.3804], # O at 48e
    ]
    wyckoff_multiplicities = [8, 24, 48]

    # Generate full set of sites based on Wyckoff positions
    full_species = []
    full_coords = []
    for sp, coord, mult in zip(species, coords, wyckoff_multiplicities):
        # Generate symmetry equivalent positions
        structure = Structure.from_spacegroup("Ia-3", lattice, [sp], [coord])
        full_species.extend([site.species_string for site in structure] * (mult // len(structure)))
        full_coords.extend([site.frac_coords for site in structure] * (mult // len(structure)))

    # Create structure
    structure = Structure(lattice, full_species, full_coords)

    # Write to CIF
    cif_writer = CifWriter(structure)
    cif_writer.write_file("pymatgen_delta_Bi2O3.cif")

    return structure

def ase_code():
    from ase import Atoms
    from ase.io import write
    from ase.spacegroup import crystal

    # Define lattice parameters
    a = 11.14  # Angstroms

    # Define atomic positions and symbols
    symbols = ["Bi", "Bi", "O"]
    basis = [
        (0.25, 0.25, 0.25),       # Bi(1) at 8b
        (0.4703, 0.0, 0.25),      # Bi(2) at 24d
        (0.3936, 0.1545, 0.3804), # O at 48e
    ]

    # Define space group and create the structure
    spacegroup = "Ia-3"
    atoms = crystal(
        symbols=symbols,
        basis=basis,
        spacegroup=spacegroup,
        cellpar=[a, a, a, 90, 90, 90]
    )

    # Write to CIF
    write("ase_delta_Bi2O3.cif", atoms)

    return atoms