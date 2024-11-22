# uncompyle6 version 3.9.1
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.11.5 | packaged by Anaconda, Inc. | (main, Sep 11 2023, 13:26:23) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: PyInstaller\hooks\rthooks\pyi_rth_pkgres.py


def _pyi_rthook():
    import os, pathlib, sys, pkg_resources
    from pyimod02_importers import PyiFrozenImporter
    SYS_PREFIX = pathlib.PurePath(sys._MEIPASS)

    class _TocFilesystem:
        __doc__ = "\n        A prefix tree implementation for embedded filesystem reconstruction.\n        "

        def __init__(self, toc_files, toc_dirs=None):
            toc_dirs = toc_dirs or []
            self._tree = dict()
            for path in toc_files:
                path = pathlib.PurePath(path)
                current = self._tree
                for component in path.parts[None[:-1]]:
                    current = current.setdefault(component, {})

                current[path.parts[-1]] = ""

            for path in toc_dirs:
                path = pathlib.PurePath(path)
                current = self._tree
                for component in path.parts:
                    current = current.setdefault(component, {})

        def _get_tree_node(self, path):
            path = pathlib.PurePath(path)
            current = self._tree
            for component in path.parts:
                if component not in current:
                    return
                current = current[component]

            return current

        def path_exists(self, path):
            node = self._get_tree_node(path)
            return node is not None

        def path_isdir(self, path):
            node = self._get_tree_node(path)
            if node is None:
                return False
            if isinstance(node, str):
                return False
            return True

        def path_listdir(self, path):
            node = self._get_tree_node(path)
            if not isinstance(node, dict):
                return []
            return list(node.keys())

    _toc_tree_cache = {}

    class PyiFrozenProvider(pkg_resources.NullProvider):
        __doc__ = "\n        Custom pkg_resources provider for PyiFrozenImporter.\n        "

        def __init__(self, module):
            super().__init__(module)
            self._pkg_path = pathlib.PurePath(module.__file__).parent
            self._embedded_tree = None

        def _init_embedded_tree(self, rel_pkg_path, pkg_name):
            data_files = []
            package_dirs = []
            for entry in self.loader.toc:
                entry_path = pathlib.PurePath(entry)
                if rel_pkg_path in entry_path.parents:
                    data_files.append(entry_path)
                elif entry.startswith(pkg_name) and self.loader.is_package(entry):
                    package_dir = (pathlib.PurePath)(*entry.split("."))
                    package_dirs.append(package_dir)

            return _TocFilesystem(data_files, package_dirs)

        @property
        def embedded_tree(self):
            if self._embedded_tree is None:
                rel_pkg_path = self._pkg_path.relative_to(SYS_PREFIX)
                pkg_name = ".".join(rel_pkg_path.parts)
                if pkg_name not in _toc_tree_cache:
                    _toc_tree_cache[pkg_name] = self._init_embedded_tree(rel_pkg_path, pkg_name)
                self._embedded_tree = _toc_tree_cache[pkg_name]
            return self._embedded_tree

        def _normalize_path(self, path):
            return pathlib.Path(os.path.abspath(path))

        def _is_relative_to_package(self, path):
            return path == self._pkg_path or self._pkg_path in path.parents

        def _has(self, path):
            path = self._normalize_path(path)
            if not self._is_relative_to_package(path):
                return False
            if path.exists():
                return True
            rel_path = path.relative_to(SYS_PREFIX)
            return self.embedded_tree.path_exists(rel_path)

        def _isdir(self, path):
            path = self._normalize_path(path)
            if not self._is_relative_to_package(path):
                return False
            rel_path = path.relative_to(SYS_PREFIX)
            node = self.embedded_tree._get_tree_node(rel_path)
            if node is None:
                return path.is_dir()
            return not isinstance(node, str)

        def _listdir(self, path):
            path = self._normalize_path(path)
            if not self._is_relative_to_package(path):
                return []
            rel_path = path.relative_to(SYS_PREFIX)
            content = self.embedded_tree.path_listdir(rel_path)
            if path.is_dir():
                path = str(path)
                content = list(set(content + os.listdir(path)))
            return content

    pkg_resources.register_loader_type(PyiFrozenImporter, PyiFrozenProvider)


_pyi_rthook()
del _pyi_rthook
