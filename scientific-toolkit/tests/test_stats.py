# -*- coding: utf-8 -*-
"""Valeurs de référence : R / SciPy / tables statistiques classiques."""
import math, pathlib, sys, unittest
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from scitk.audit import stats as S


class TestDistributions(unittest.TestCase):
    def test_t(self):
        # scipy.stats.t.sf : t=2.0, df=10 -> 0.03669 ; bilatéral 0.07339
        self.assertAlmostEqual(S.t_two_sided_p(2.0, 10), 0.0733880, places=6)
        self.assertAlmostEqual(S.t_two_sided_p(0.0, 5), 1.0, places=9)
        self.assertAlmostEqual(S.t_two_sided_p(3.169, 10), 0.01000, places=4)
        self.assertAlmostEqual(S.t_two_sided_p(-2.228, 10), 0.05000, places=4)

    def test_f(self):
        # F=4.0, df1=2, df2=30 -> 0.02904
        self.assertAlmostEqual(S.f_sf(4.0, 2, 30), 0.028845, places=6)  # 1-(1-8/38)^15
        self.assertAlmostEqual(S.f_sf(1.0, 1, 1), 0.5, places=6)
        self.assertAlmostEqual(S.f_sf(3.0, 5, 100), 0.0144926, places=6)

    def test_chi2(self):
        self.assertAlmostEqual(S.chi2_sf(3.841, 1), 0.05000, places=4)
        self.assertAlmostEqual(S.chi2_sf(5.991, 2), 0.05000, places=4)
        self.assertAlmostEqual(S.chi2_sf(18.307, 10), 0.05000, places=4)
        self.assertAlmostEqual(S.chi2_sf(0.0, 3), 1.0)

    def test_norm(self):
        self.assertAlmostEqual(S.z_two_sided_p(1.96), 0.05000, places=4)
        self.assertAlmostEqual(S.norm_ppf(0.975), 1.959964, places=6)
        self.assertAlmostEqual(S.p_to_z(0.05), 1.959964, places=5)


class TestEffets(unittest.TestCase):
    def test_conversions(self):
        self.assertAlmostEqual(S.t_to_r(2.0, 28), 0.353553, places=6)
        self.assertAlmostEqual(S.f_to_eta2(4.0, 2, 30), 0.210526, places=6)
        self.assertAlmostEqual(S.chi2_to_v(4.0, 100, 2), 0.2, places=6)
        self.assertAlmostEqual(S.f_to_f2(4.0, 2, 30), 0.266667, places=6)

    def test_binomial(self):
        # P(X>=8 | n=10, p=.5) = 0.0546875
        self.assertAlmostEqual(S.binomial_sf(8, 10, 0.5), 0.0546875, places=9)
        self.assertAlmostEqual(S.binomial_two_sided(9, 10, 0.5), 0.021484375, places=9)

    def test_chi2_uniform(self):
        chi2, p, df = S.chisq_uniform_test([10] * 10)
        self.assertAlmostEqual(chi2, 0.0)
        self.assertEqual(df, 9)
        chi2, p, df = S.chisq_uniform_test([50, 50, 50, 50, 50, 50, 50, 50, 50, 50])
        self.assertAlmostEqual(p, 1.0)

    def test_p_interval(self):
        lo, hi = S.p_interval(0.03, 3)
        self.assertAlmostEqual(lo, 0.0295)
        self.assertAlmostEqual(hi, 0.0305)


if __name__ == "__main__":
    unittest.main(verbosity=2)
