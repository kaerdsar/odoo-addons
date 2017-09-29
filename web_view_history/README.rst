================
Web View History
================

This module generates inherited views based on modified arch. Instead of update the existing view creates a new inherited view. This implementation is still a test version.

This feature is useful to handle history versions of a view.

The module uses a C++ library to detect changes in XML based on the paper http://pages.cs.wisc.edu/~yuanwang/papers/xdiff.pdf.


Usage
=====

To install this module, you need to:

* sudo apt-get install libxerces-c-dev
* Download the repository from https://github.com/kaerdsar/xdiff-c
* Install it using: 'g++ -o xdiff *.cpp -lxerces-c --std=c++11' (do not use the make command)
* Copy the binary xdiff generated file in /usr/local/bin/

To use the module, you need to:

* Install the addon in Odoo database
* There is a new boolean field in the model ir.ui.view called enable_history, if you set this field to True all updates will be saved as inherited views.


Known issues / Roadmap
======================

* The algorithm used does not take care of position of siblings elements. If you only change the position of the element in a view, the algorithm returns not changes in the XML.
