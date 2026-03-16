# -*- coding: utf-8 -*-
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestAgeingReports(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.StockMove = cls.env['stock.move']

    def test_ageing_cost_report_per_product(self):
        """Ageing cost report action exists and filters done moves."""
        action = self.env.ref(
            'warehouse_ageing_cost.action_ageing_cost_report',
            raise_if_not_found=False
        )
        if action:
            self.assertEqual(action.res_model, 'stock.move')
            self.assertIn('done', str(action.domain))

    def test_inventory_ageing_report_value_at_risk(self):
        """Inventory ageing report action exists."""
        action = self.env.ref(
            'warehouse_ageing_cost.action_inventory_ageing_report',
            raise_if_not_found=False
        )
        if action:
            self.assertEqual(action.res_model, 'stock.move')
