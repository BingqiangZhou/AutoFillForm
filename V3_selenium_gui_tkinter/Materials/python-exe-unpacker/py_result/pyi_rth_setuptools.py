# uncompyle6 version 3.9.1
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.11.5 | packaged by Anaconda, Inc. | (main, Sep 11 2023, 13:26:23) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: PyInstaller\hooks\rthooks\pyi_rth_setuptools.py


def _pyi_rthook():

    def _install_setuptools_distutils_hack():
        import os, setuptools
        setuptools_major = int(setuptools.__version__.split(".")[0])
        default_value = "stdlib" if setuptools_major < 60 else "local"
        if os.environ.get("SETUPTOOLS_USE_DISTUTILS", default_value) == "local":
            import _distutils_hack
            _distutils_hack.add_shim()

    try:
        _install_setuptools_distutils_hack()
    except Exception:
        pass


_pyi_rthook()
del _pyi_rthook
