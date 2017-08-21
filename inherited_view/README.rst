===============
Inherited Views
===============

This module generates inherited views based on modified arch. Instead of update the existing view creates a new inherited view. This implementation is still a test version.

This feature is useful to handle history versions of a view.

The module uses a C++ library to detect changes in XML based on the paper http://pages.cs.wisc.edu/~yuanwang/papers/xdiff.pdf.


Usage
=====

To install this module, you need to:

* sudo apt-get install libxerces-c-dev
* Download the repository from https://github.com/ateijelo/xdiff-c
* Install it using: 'g++ -o xdiff *.cpp -lxerces-c --std=c++11' (do not use the make command)
* Copy the binary xdiff generated file in /usr/local/bin/

To use the module, you need to:

* Install the addon in Odoo database
* Pass the context 'save_as_inherited_view' to the write method of ir.ui.view model in the context you want to generate inherited view instead of update the current view.

Example for website pages:
...
from odoo import models

class IrUiView(model.Model):
   _inherit = 'ir.ui.view'

   @api.multi
   def save(self, value, xpath):
      self = self.with_context(save_as_inherited_view=True)
      return super(IrUiView, self).save(value, xpath)
...


Known issues / Roadmap
======================

* The algorithm used does not take care of position of siblings elements. If you only change the position of the element in a view, the algorithm returns not changes in the XML.
