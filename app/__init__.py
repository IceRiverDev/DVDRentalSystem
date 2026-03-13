from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("dvdrental-api")
except PackageNotFoundError:
    # Running from source without installing the package
    __version__ = "0.0.0+dev"
