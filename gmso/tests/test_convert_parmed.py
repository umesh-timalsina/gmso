import unyt as u
import pytest

from gmso.external.convert_parmed import from_parmed
from gmso.tests.base_test import BaseTest
from gmso.utils.io import get_fn
from gmso.utils.testing import allclose
from gmso.utils.io import get_fn, import_, has_parmed


if has_parmed:
    pmd = import_('parmed')

@pytest.mark.skipif(not has_parmed, reason="ParmEd is not installed")
class TestConvertParmEd(BaseTest):
    def test_from_parmed_basic(self, angles):
        struc = pmd.load_file(get_fn('ethane.mol2'), structure=True)
        top = from_parmed(struc)
        for site in top.sites:
            assert site.atom_type is None
        for connection in top.connections:
            assert connection.connection_type is None
        assert top.n_sites == 8
        assert top.n_bonds == 7

        assert top.box is not None
        lengths = u.nm * [0.714, 0.7938, 0.6646]
        assert allclose(top.box.lengths, lengths)
        assert allclose(top.box.angles, angles)

    def test_from_parmed_parametrized_structure(self, angles):
        struc = pmd.load_file(get_fn('ethane.top'), xyz=get_fn('ethane.gro'))
        top = from_parmed(struc)
        assert top.n_sites == 8
        assert top.n_bonds == 7
        assert top.n_angles == 12
        assert top.n_connections == 19

        for site in top.sites:
            assert site.atom_type is not None
            assert site.charge is not None

        for connection in top.connections:
            assert connection.connection_type is not None

        assert top.box is not None
        lengths = u.nm * [0.714, 0.7938, 0.6646]
        assert allclose(top.box.lengths, lengths)
        assert allclose(top.box.angles, angles)
