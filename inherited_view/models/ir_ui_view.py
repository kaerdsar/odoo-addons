# -*- coding: utf-8 -*-
from lxml import etree
from openerp import api, models
from openerp.addons.inherited_view.tools.xdiff import calculate_xml_diff


class IrUiView(models.Model):
    _inherit = "ir.ui.view"

    @api.multi
    def write(self, values):
        if self.env.context.get('save_as_inherited_view', False) \
                and 'arch' in values:
            for record in self:
                diff_arch = calculate_xml_diff(
                    record.arch, values['arch'], record.id
                )
                if diff_arch:
                    inherited_arch = self.create_inherited_arch(diff_arch)
                    self.create({
                        'name': 'inherited.%s' % record.name,
                        'model': record.model,
                        'inherit_id': record.id,
                        'arch': '<data>%s</data>' % inherited_arch
                    })
            return True
        else:
            return super(IrUiView, self).write(values)

    def create_inherited_arch(self, diff_arch):
        inherited_arch = ''
        tree = etree.fromstring(diff_arch)
        for element in tree.xpath('//processing-instruction()'):

            parent = element.getparent()
            xpath = parent.getroottree().getpath(parent)

            tag = False
            pi_words = element.text.split(' ')
            if pi_words and pi_words[0] != 'FROM':
                tag = pi_words[0]

            method = '_parse_' + element.target.lower()
            inherited_arch += getattr(self, method)(
                tag, element, parent, xpath
            )

        return inherited_arch

    def _parse_insert(self, tag, element, parent, xpath):
        if tag == parent.tag:
            etree.strip_tags(parent, element.tag)
            element = parent
            parent = parent.getparent()

            children = len(parent.getchildren())
            index = parent.index(element)
            if children == 1:
                position = 'inside'
                xpath = parent.getroottree().getpath(parent)
            elif index > 0:
                position = 'after'
                previous_element = element.getprevious()
                xpath = parent.getroottree().getpath(previous_element)
            else:
                position = 'before'
                next_element = element.getnext()
                xpath = parent.getroottree().getpath(next_element)

            return self._build_xpath_expr(
                xpath,
                position,
                etree.tostring(element)
            )
        else:
            attribute = tag
            return self._build_xpath_expr(
                xpath,
                'attributes',
                '<attribute name="%s">%s</attribute>'
                % (attribute, parent.attrib[attribute])
            )

    def _parse_update(self, tag, element, parent, xpath):
        if not tag or tag == parent.tag:
            etree.strip_tags(parent, element.tag)
            return self._build_xpath_expr(
                xpath,
                'replace',
                etree.tostring(parent)
            )
        else:
            attribute = tag
            return self._build_xpath_expr(
                xpath,
                'attributes',
                '<attribute name="%s">%s</attribute>'
                % (attribute, parent.attrib[attribute])
            )

    def _parse_delete(self, tag, element, parent, xpath):
        if tag == parent.tag:
            return self._build_xpath_expr(xpath, 'replace')
        return ''

    @api.model
    def _build_xpath_expr(self, path, position, content=''):
        return """
                <xpath expr="%s" position="%s">
                    %s
                </xpath>
            """ % (path, position, content)

