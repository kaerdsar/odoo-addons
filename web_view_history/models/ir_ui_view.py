# -*- coding: utf-8 -*-
from lxml import etree
from openerp import api, models
from openerp.addons.web_view_history.tools.xdiff import XDiff


class IrUiView(models.Model):
    _inherit = "ir.ui.view"

    enable_history = fields.Boolean('Enable History')
    history = fields.Boolean('History')
    active = fields.Boolean('Active')

    @api.multi
    def write(self, values):
        if 'arch' in values:
            for record in self:
                if record.enable_history and not record.inherit_id:
                    record.create_version(values['arch'])
                else:
                    super(IrUiView, record).write(values)
            return True
        else:
            return super(IrUiView, self).write(values)

    def create_version(self, arch, inherited=False):
        current = self.search([
            ('history', '=', True),
            ('inherit_id', '=', self.id)
        ], limit=1)
        if current:
            current.write({'active': False})
        if not inherited:
            arch = self.generate_inherited_view_arch(arch)
        self.create({
            'name': 'inherited.%s' % self.name,
            'model': self.model,
            'inherit_id': self.id,
            'arch': '<data>%s</data>' % arch,
            'history': True
        })

    def restore_version(self):
        self.inherit_id.create_version(self.arch, inherited=True)

    def generate_inherited_view_arch(self, arch):
        diff = XDiff()
        return diff.calculate_xml_diff(self.arch, arch)

    def apply_view_inheritance(self, cr, uid, source, source_id, model,
                               root_id=None, context=None):
        if context is None: context = {}
        if root_id is None:
            root_id = source_id
        sql_inherit = self.get_inheriting_views_arch(
            cr, uid, source_id, model, context=context
        )
        for (specs, view_id) in sql_inherit:
            specs_tree = etree.fromstring(specs.encode('utf-8'))
            view = self.browse(cr, uid, view_id)
            if not view.history and context.get('inherit_branding'):
                self.inherit_branding(specs_tree, view_id, root_id)
            source = self.apply_inheritance_specs(
                cr, uid, source, specs_tree, view_id, context=context
            )
            source = self.apply_view_inheritance(
                cr, uid, source, view_id, model,
                root_id=root_id, context=context
            )
        return source

