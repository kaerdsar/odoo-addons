# -*- coding: utf-8 -*-
import subprocess
from lxml import etree, html


class XDiff(object):

    def calculate_xml_diff(self, origin_arch, target_arch):
        command = ['xdiff', origin_arch, target_arch]
        diff_arch = subprocess.check_output(command)
        diff_arch = self.clean_arch(diff_arch)
        return self.parse_diff_arch(diff_arch)

    def parse_diff_arch(self, diff_arch):
        inherited_arch = ''
        tree = etree.fromstring(diff_arch)
        for element in tree.xpath('//processing-instruction()'):

            parent = element.getparent()
            if parent:
                xpath = parent.getroottree().getpath(parent)

                tag = False
                pi_words = element.text.split(' ')
                if pi_words and pi_words[0] != 'FROM':
                    tag = pi_words[0].replace('?', '')

                method = '_parse_' + element.target.lower()
                inherited_arch += getattr(self, method)(
                    tag, element, parent, xpath
                )

        return inherited_arch

    def clean_arch(self, arch):
        html_parser = html.HTMLParser(encoding='utf-8')
        arch_html = html.fromstring(arch, parser=html_parser)

        xml_parser = etree.XMLParser(encoding='utf-8', remove_blank_text=True)
        arch_no_whitespace = etree.fromstring(
            etree.tostring(arch_html, encoding='utf-8'), parser=xml_parser
        )

        return etree.tostring(arch_no_whitespace, pretty_print=True)

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
        elif tag in parent.attrib:
            attribute = tag
            return self._build_xpath_expr(
                xpath,
                'attributes',
                '<attribute name="%s">%s</attribute>'
                % (attribute, parent.attrib[attribute])
            )
        else:
            return ''

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
        else:
            attribute = tag
            return self._build_xpath_expr(
                xpath,
                'attributes',
                '<attribute name="%s"></attribute>'
                % attribute
            )

    def _build_xpath_expr(self, path, position, content=''):
        return """
                <xpath expr="%s" position="%s">
                    %s
                </xpath>
            """ % (path, position, content)
