# -*- coding: utf-8 -*-
from odoo.tests import TransactionCase, tagged
from odoo.exceptions import ValidationError


@tagged('post_install', '-at_install')
class TestProductCategory(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ProductCategory = cls.env['product.category']

    def test_daily_storage_rate_default(self):
        """Daily storage rate defaults to 0."""
        categ = self.ProductCategory.create({
            'name': 'Test Category',
        })
        self.assertEqual(categ.daily_storage_rate, 0.0)

    def test_handling_fee_optional(self):
        """Handling fee is optional and defaults to 0."""
        categ = self.ProductCategory.create({
            'name': 'Test Category',
            'daily_storage_rate': 1.5,
        })
        self.assertEqual(categ.handling_dispatch_fee, 0.0)
        categ.handling_dispatch_fee = 5.0
        self.assertEqual(categ.handling_dispatch_fee, 5.0)

    def test_ageing_in_cogs_configurable(self):
        """Ageing in COGS is configurable per category."""
        categ = self.ProductCategory.create({
            'name': 'Test Category',
            'ageing_in_cogs': True,
        })
        self.assertTrue(categ.ageing_in_cogs)
        categ.ageing_in_cogs = False
        self.assertFalse(categ.ageing_in_cogs)

    def test_negative_storage_rate_validation(self):
        """Negative daily storage rate raises ValidationError."""
        with self.assertRaises(ValidationError):
            self.ProductCategory.create({
                'name': 'Test Category',
                'daily_storage_rate': -1.0,
            })
