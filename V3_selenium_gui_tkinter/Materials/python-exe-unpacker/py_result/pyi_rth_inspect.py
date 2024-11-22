# uncompyle6 version 3.9.1
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.11.5 | packaged by Anaconda, Inc. | (main, Sep 11 2023, 13:26:23) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: PyInstaller\hooks\rthooks\pyi_rth_inspect.py


def _pyi_rthook():
    import inspect, os, sys
    _orig_inspect_getsourcefile = inspect.getsourcefile

    def _pyi_getsourcefile(object):
        filename = inspect.getfile(object)
        main_file = os.path.isabs(filename) or getattr(sys.modules["__main__"], "__file__", None)
        if main_file:
            if filename == os.path.basename(main_file):
                return main_file
        elif filename.endswith(".py"):
            filename = os.path.normpath(os.path.join(sys._MEIPASS, filename + "c"))
            if filename.startswith(sys._MEIPASS):
                return filename
            else:
                if filename.startswith(sys._MEIPASS):
                    if filename.endswith(".pyc"):
                        return filename
        return _orig_inspect_getsourcefile(object)

    inspect.getsourcefile = _pyi_getsourcefile


_pyi_rthook()
del _pyi_rthook
