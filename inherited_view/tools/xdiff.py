# -*- coding: utf-8 -*-
import os
import shutil
from subprocess import call


def calculate_xml_diff(origin_arch, target_arch, view_id):
    diff_arch = False

    folder = 'diff/%s' % str(view_id)
    os.makedirs(folder)

    origin_path = '%s/origin.xml' % folder
    target_path = '%s/target.xml' % folder
    diff_path = '%s/diff.xml' % folder

    with open(origin_path, 'w') as origin:
        origin.write(origin_arch.encode('utf8'))

    with open(target_path, 'w') as target:
        target.write(target_arch.encode('utf8'))

    call('xdiff %s %s %s' % (origin_path, target_path, diff_path), shell=True)

    if os.path.exists(diff_path):
        with open(diff_path) as diff:
            diff_arch = diff.read()

    shutil.rmtree(folder)

    return diff_arch
