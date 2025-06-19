from functools import lru_cache
from .schema import AppConfig
from .loader import ConfigLoader

_config_loader = ConfigLoader()

@lru_cache()
def get_config() -> AppConfig:
    """Get the application configuration (cached)"""
    return _config_loader.load_config()

def reload_config() -> AppConfig:
    """Force reload configuration"""
    get_config.cache_clear()
    return _config_loader.load_config(force_reload=True)
