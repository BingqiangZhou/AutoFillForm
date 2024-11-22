# uncompyle6 version 3.9.1
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.11.5 | packaged by Anaconda, Inc. | (main, Sep 11 2023, 13:26:23) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: PyInstaller\hooks\rthooks\pyi_rth_win32comgenpy.py


def _pyi_rthook():
    import atexit, os, shutil, tempfile
    supportdir = tempfile.mkdtemp()
    genpydir = os.path.join(supportdir, "gen_py")
    try:
        os.makedirs(genpydir)
        atexit.register((shutil.rmtree), supportdir, ignore_errors=True)
    except OSError:
        pass

    import win32com
    win32com.__gen_path__ = genpydir
    if hasattr(win32com, "__loader__"):
        del win32com.__loader__
    import win32com.gen_py
    win32com.gen_py.__path__.insert(0, genpydir)


_pyi_rthook()
del _pyi_rthook
