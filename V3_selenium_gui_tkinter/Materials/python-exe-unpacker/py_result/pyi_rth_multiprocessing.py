# uncompyle6 version 3.9.1
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.11.5 | packaged by Anaconda, Inc. | (main, Sep 11 2023, 13:26:23) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: PyInstaller\hooks\rthooks\pyi_rth_multiprocessing.py


def _pyi_rthook():
    import os, sys, threading, multiprocessing, multiprocessing.spawn
    from subprocess import _args_from_interpreter_flags
    multiprocessing.process.ORIGINAL_DIR = None

    def _freeze_support():
        if len(sys.argv) >= 2:
            if sys.argv[-2] == "-c":
                if sys.argv[-1].startswith(('from multiprocessing.semaphore_tracker import main',
                                            'from multiprocessing.resource_tracker import main',
                                            'from multiprocessing.forkserver import main')):
                    if set(sys.argv[1[:-2]]) == set(_args_from_interpreter_flags()):
                        exec(sys.argv[-1])
                        sys.exit()
        if multiprocessing.spawn.is_forking(sys.argv):
            kwds = {}
            for arg in sys.argv[2[:None]]:
                name, value = arg.split("=")
                if value == "None":
                    kwds[name] = None
                else:
                    kwds[name] = int(value)

            (multiprocessing.spawn.spawn_main)(**kwds)
            sys.exit()

    multiprocessing.freeze_support = multiprocessing.spawn.freeze_support = _freeze_support

    class FrozenSupportMixIn:
        _lock = threading.Lock()

        def __init__(self, *args, **kw):
            with self._lock:
                os.putenv("_MEIPASS2", sys._MEIPASS)
                try:
                    (super().__init__)(*args, **kw)
                finally:
                    if hasattr(os, "unsetenv"):
                        os.unsetenv("_MEIPASS2")
                    else:
                        os.putenv("_MEIPASS2", "")

    if sys.platform.startswith("win"):
        from multiprocessing import popen_spawn_win32

        class _SpawnPopen(FrozenSupportMixIn, popen_spawn_win32.Popen):
            pass

        popen_spawn_win32.Popen = _SpawnPopen
    else:
        from multiprocessing import popen_spawn_posix
        from multiprocessing import popen_forkserver

        class _SpawnPopen(FrozenSupportMixIn, popen_spawn_posix.Popen):
            pass

        class _ForkserverPopen(FrozenSupportMixIn, popen_forkserver.Popen):
            pass

        popen_spawn_posix.Popen = _SpawnPopen
        popen_forkserver.Popen = _ForkserverPopen


_pyi_rthook()
del _pyi_rthook
