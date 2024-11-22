# uncompyle6 version 3.9.1
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.11.5 | packaged by Anaconda, Inc. | (main, Sep 11 2023, 13:26:23) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: _pyinstaller_hooks_contrib\hooks\rthooks\pyi_rth_traitlets.py
import traitlets.traitlets

def _disabled_deprecation_warnings(method, cls, method_name, msg):
    pass


traitlets.traitlets._deprecated_method = _disabled_deprecation_warnings
