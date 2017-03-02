# -*- coding: utf-8 -*-
#   Copyright (C) 2015 Akretion (http://www.akretion.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    bom_line_ids = fields.One2many(
        'mrp.bom.line',
        'product_tmpl_id',
        string='Bom Line',
        help='If you product is manufactured you can select'
             'here the componant to product them')

    @api.model
    def _extract_bom_line(self, vals):
        return vals.pop('bom_line_ids', {})

    @api.multi
    def _prepare_bom_vals(self, vals):
        return {
            'product_tmpl_id': self.id,
            'bom_line_ids': vals,
        }

    @api.multi
    def _process_bom_vals(self, vals):
        for record in self:
            if record.bom_ids:
                record.bom_ids[0].write({'bom_line_ids': vals})
            else:
                record.env['mrp.bom'].create(self._prepare_bom_vals(vals))

    @api.model
    def create(self, vals):
        bom_vals = self._extract_bom_line(vals)
        record = super(ProductTemplate, self).create(vals)
        if bom_vals:
            record._process_bom_vals(bom_vals)
        return record

    @api.multi
    def write(self, vals):
        bom_vals = self._extract_bom_line(vals)
        res = super(ProductTemplate, self).write(vals)
        if bom_vals:
            self._process_bom_vals(bom_vals)
        return res

    @api.multi
    def unlink(self):
        for record in self:
            if record.bom_ids:
                record.bom_ids.unlink()
        return super(ProductTemplate, self).unlink()
