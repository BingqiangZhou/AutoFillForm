# uncompyle6 version 3.9.1
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.11.5 | packaged by Anaconda, Inc. | (main, Sep 11 2023, 13:26:23) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: PyInstaller\hooks\rthooks\pyi_rth__tkinter.py


def _pyi_rthook():
    import os, sys
    tcldir = os.path.join(sys._MEIPASS, "tcl")
    tkdir = os.path.join(sys._MEIPASS, "tk")
    is_darwin = sys.platform == "darwin"
    if os.path.isdir(tcldir):
        os.environ["TCL_LIBRARY"] = tcldir
    else:
        if not is_darwin:
            raise FileNotFoundError('Tcl data directory "%s" not found.' % tcldir)
        elif os.path.isdir(tkdir):
            os.environ["TK_LIBRARY"] = tkdir
        else:
            if not is_darwin:
                raise FileNotFoundError('Tk data directory "%s" not found.' % tkdir)


_pyi_rthook()
del _pyi_rthook
