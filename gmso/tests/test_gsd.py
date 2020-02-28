import unyt as u
import pytest

from gmso.formats.gsd import write_gsd
from gmso.external.convert_parmed import from_parmed
from gmso.tests.base_test import BaseTest
from gmso.utils.io import get_fn
from gmso.utils.io import import_, has_gsd, has_parmed


if has_parmed:
    pmd = import_('parmed')

@pytest.mark.skipif(not has_gsd, reason="gsd is not installed")
@pytest.mark.skipif(not has_parmed, reason="ParmEd is not installed")
class TestGsd(BaseTest):
    # TODO: Have these tests not depend on parmed
    def test_write_gsd(self):
        top = from_parmed(pmd.load_file(get_fn('ethane.top'),
            xyz=get_fn('ethane.gro')))

        write_gsd(top, 'out.gsd')

    def test_write_gsd_non_orthogonal(self):
        top = from_parmed(pmd.load_file(get_fn('ethane.top'),
            xyz=get_fn('ethane.gro')))
        top.box.angles = u.degree * [90, 90, 120]

        write_gsd(top, 'out.gsd')
