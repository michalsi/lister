try:
    from importlib import metadata
    __version__ = metadata.version("files_lister")
except metadata.PackageNotFoundError:
    __version__ = "unknown"