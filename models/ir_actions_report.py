# -*- coding: utf-8 -*-

from odoo import api, fields, models
from reportlab.graphics.barcode import createBarcodeImageInMemory
from odoo.exceptions import UserError
import reportlab
import base64


class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    # All this code is based on the original method to produce barcodes
    @api.model
    def svg_barcode(self, barcode_type, value, width=300, height=30, humanreadable=0):
        """ Create a SVG barcode image.

        Returns a base64 svg image ready to put it on a `src` attribute of an `<img>` tag
        """
        if reportlab.__version__ >= '3.5.49':
            if barcode_type == 'UPCA' and len(value) in (11, 12, 13):
                barcode_type = 'EAN13'
                if len(value) in (11, 12):
                    value = '0%s' % value
            try:
                width, height, humanreadable = int(width), int(height), bool(int(humanreadable))
                rst = createBarcodeImageInMemory(barcode_type, value=value, format='svg', width=width, height=height,
                    humanReadable=humanreadable)
                e = base64.b64encode(bytes(rst, 'ascii'))
                return 'data:image/svg+xml;base64,' + str(e)[2:-1]
            except (ValueError, AttributeError):
                if barcode_type == 'Code128':
                    raise ValueError("Cannot convert into svg barcode.")
                else:
                    return self.svg_barcode('Code128', value, width=width, height=height, humanreadable=humanreadable)
        else:
            user_error = (f'An earlier version of reportlab is installed: {reportlab.__version__} \nVersion 3.5.49 is needed.' +
            'See the readme (installation) of the module for more information')
            raise UserError(user_error)
    

class IrQWeb(models.AbstractModel):
    _inherit = 'ir.qweb'

    # with this method we automate the rendering proccess to change all the regular barcodes to the customs svg
    def _compile_node(self, el, options):
        if el.tag == "img" and any(((att=='t-att-src') and el.attrib[att].startswith("'/report/barcode/") and (' % ' in el.attrib[att])) for att in el.attrib):
            barcode_before = el.attrib.pop('t-att-src')
            el.set('t-att-src', "request.env['ir.actions.report'].svg_barcode" + barcode_before.split(' % ')[1])
        return super(IrQWeb, self)._compile_node(el, options)
