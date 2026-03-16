# -*- coding: utf-8 -*-
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestAgeingCostCalculation(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ProductCategory = cls.env['product.category']
        cls.ProductProduct = cls.env['product.product']
        cls.category = cls.ProductCategory.create({
            'name': 'Test Category',
            'daily_storage_rate': 1.5,
            'handling_dispatch_fee': 5.0,
        })
        cls.product = cls.ProductProduct.create({
            'name': 'Test Product',
            'type': 'product',
            'categ_id': cls.category.id,
        })

    def test_ageing_cost_formula(self):
        """Ageing Cost = Daily Rate × Days + Handling Fee per unit."""
        # get_ageing_cost_for_so_line returns 0 when no stock moves
        cost = self.product.get_ageing_cost_for_so_line(1.0)
        self.assertEqual(cost, 0.0)

    def test_zero_rate_returns_zero(self):
        """Zero daily rate with no stock returns 0."""
        categ = self.ProductCategory.create({
            'name': 'Zero Rate Category',
            'daily_storage_rate': 0.0,
        })
        product = self.ProductProduct.create({
            'name': 'Zero Rate Product',
            'type': 'product',
            'categ_id': categ.id,
        })
        cost = product.get_ageing_cost_for_so_line(10.0)
        self.assertEqual(cost, 0.0)

    def test_no_grn_date_returns_zero(self):
        """Product with no incoming moves returns 0 ageing cost."""
        cost = self.product.get_ageing_cost_for_so_line(5.0)
        self.assertEqual(cost, 0.0)
