from ...import_assist import SubmoduleImporter as _SubmoduleImporter

_importer= _SubmoduleImporter()
_importer.import_pkgs()
_importer.inject_modules()
__all__ = _importer.all_list() # type: ignore