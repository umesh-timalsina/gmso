import numpy as np
import unyt as u

import gmso
from gmso.utils.io import import_, has_parmed


if has_parmed:
    pmd = import_('parmed')

def from_parmed(structure):
    """Convert a parmed.Structure to a gmso.Topology

    Convert a parametrized or un-parametrized parmed.Structure object to a topology.Topology.
    Specifically, this method maps Structure to Topology and Atom to Site.
    At this point, this method can only convert AtomType, BondType and AngleType.
    Conversion of DihedralType will be implement in the near future.

    Parameters
    ----------
    structure : parmed.Structure
        parmed.Structure instance that need to be converted.

    Returns
    -------
    top : gmso.Topology
    """
    msg = ("Provided argument that is not a Parmed Structure")
    assert isinstance(structure, pmd.Structure), msg

    top = gmso.Topology(name=structure.title)
    site_map = dict()
    for atom in structure.atoms:
        if isinstance(atom.atom_type, pmd.AtomType):
            atom_type = gmso.AtomType(
                name=atom.atom_type.name,
                charge=atom.atom_type.charge * u.elementary_charge,
                parameters={
                    'sigma': (atom.sigma * u.angstrom).in_units(u.nm),
                    'epsilon': atom.epsilon * u.Unit('kcal / mol')
                })
            site = gmso.Site(
                name=atom.name,
                charge=atom.charge * u.elementary_charge,
                position=([atom.xx, atom.xy, atom.xz] * u.angstrom).in_units(
                    u.nm),
                atom_type=atom_type)
        else:
            site = gmso.Site(
                name=atom.name,
                charge=atom.charge * u.elementary_charge,
                position=([atom.xx, atom.xy, atom.xz] * u.angstrom).in_units(
                    u.nm),
                atom_type=None)
        site_map[atom] = site
        top.add_site(site)
    top.update_topology()

    if np.all(structure.box):
        # This is if we choose for topology to have abox
        top.box = gmso.Box(
            (structure.box[0:3] * u.angstrom).in_units(u.nm),
            angles=u.degree * structure.box[3:6])

    for bond in structure.bonds:
        # Generate bond parameters for BondType that gets passed
        # to Bond
        if isinstance(bond.type, pmd.BondType):
            bond_params = {
                'k': (2 * bond.type.k * u.Unit('kcal / (nm**2 * mol)')),
                'r_eq': (bond.type.req * u.angstrom).in_units(u.nm)
            }
            new_connection_type = gmso.BondType(parameters=bond_params)
            top_connection = gmso.Bond(connection_members=[site_map[bond.atom1],
                site_map[bond.atom2]],
                connection_type=new_connection_type)

        # No bond parameters, make Connection with no connection_type
        else:
            top_connection = gmso.Bond(connection_members=[site_map[bond.atom1],
                site_map[bond.atom2]],
                connection_type=None)

        top.add_connection(top_connection, update_types=False)
    top.update_topology()
    print(top.n_bonds)

    for angle in structure.angles:
        # Generate angle parameters for AngleType that gets passed
        # to Angle
        if isinstance(angle.type, pmd.AngleType):
            angle_params = {
                'k': (2 * angle.type.k * u.Unit('kcal / (rad**2 * mol)')),
                'theta_eq': (angle.type.theteq * u.degree)
            }
            new_connection_type = gmso.AngleType(parameters=angle_params)
            top_connection = gmso.Angle(connection_members=[site_map[angle.atom1],
                site_map[angle.atom2], site_map[angle.atom3]],
                connection_type=new_connection_type)

        # No bond parameters, make Connection with no connection_type
        else:
            top_connection = gmso.Angle(connection_members=[site_map[angle.atom1],
                site_map[angle.atom2], site_map[angle.atom3]],
                connection_type=None)

        top.add_connection(top_connection, update_types=False)
    top.update_topology()

    # TODO: Dihedrals


    return top
