# uncompyle6 version 3.9.1
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.11.5 | packaged by Anaconda, Inc. | (main, Sep 11 2023, 13:26:23) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: PyInstaller\hooks\rthooks\pyi_rth_mplconfig.py


def _pyi_rthook():
    import atexit, os, shutil, tempfile
    configdir = tempfile.mkdtemp()
    os.environ["MPLCONFIGDIR"] = configdir
    try:
        atexit.register((shutil.rmtree), configdir, ignore_errors=True)
    except OSError:
        pass


_pyi_rthook()
del _pyi_rthook
