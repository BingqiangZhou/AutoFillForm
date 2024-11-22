# uncompyle6 version 3.9.1
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.11.5 | packaged by Anaconda, Inc. | (main, Sep 11 2023, 13:26:23) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: _pyinstaller_hooks_contrib\hooks\rthooks\pyi_rth_pywintypes.py
import sys, os
pywin32_system32_path = os.path.join(sys._MEIPASS, "pywin32_system32")
if os.path.isdir(pywin32_system32_path):
    if pywin32_system32_path not in sys.path:
        sys.path.append(pywin32_system32_path)
del pywin32_system32_path
