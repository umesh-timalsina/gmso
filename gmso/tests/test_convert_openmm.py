import unyt as u
import numpy as np
import pytest

from gmso.core.box import Box
from gmso.external.convert_openmm import to_openmm
from gmso.tests.base_test import BaseTest
from gmso.utils.io import import_, has_openmm, has_simtk_unit


if has_openmm and has_simtk_unit:
    simtk_unit = import_('simtk.unit')

@pytest.mark.skipif(not has_openmm, reason="OpenMM is not installed")
@pytest.mark.skipif(not has_simtk_unit, reason="SimTK is not installed")
class TestOpenMM(BaseTest):
    def test_openmm_modeller(self, topology_site):
        to_openmm(topology_site(), openmm_object='modeller')

    def test_openmm_topology(self, topology_site):
        to_openmm(topology_site(), openmm_object='topology')

    def test_n_atoms(self, topology_site):
        top = topology_site(sites=10)
        n_topology_sites = len(top.sites)
        modeller = to_openmm(top, openmm_object='modeller')
        n_modeller_atoms = len([i for i in modeller.topology.atoms()])

        assert n_topology_sites == n_modeller_atoms

    def test_box_dims(self, topology_site):
        top = topology_site(sites=10)
        n_topology_sites = len(top.sites)
        omm_top = to_openmm(top)
        topology_lengths = top.box.lengths
        omm_lengths = omm_top.getUnitCellDimensions()

        assert np.allclose(topology_lengths.value, omm_lengths._value)

    def test_particle_positions(self, topology_site):
        top = topology_site()
        top.sites[0].position = (1,1,1) * u.nanometer
        omm_top = to_openmm(top, openmm_object='modeller')

        assert np.allclose(omm_top.positions._value, top.positions.value)

    def test_position_units(self, topology_site):
        top = topology_site(sites=10)
        top.box = Box(lengths=[1,1,1])

        n_topology_sites = len(top.sites)
        omm_top = to_openmm(top, openmm_object='modeller')

        assert isinstance(omm_top.positions.unit, type(simtk_unit.nanometer))
