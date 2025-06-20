import yaml
import os
from pathlib import Path
from typing import Dict, Any, Optional
from .schema import AppConfig

def deep_merge(base: Dict, updates: Dict) -> Dict:
    result = base.copy()
    for key, value in updates.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result

class ConfigLoader:
    """Handles loading configuration from multiple sources"""
    def __init__(self, config_dir: Path = None):
        # Allow override by CONFIG_DIR env var, else find 'config' up the tree
        env_dir = os.getenv("CONFIG_DIR")
        if env_dir:
            self.config_dir = Path(env_dir)
        else:
            # Search up from CWD for 'config' dir
            p = Path.cwd()
            found = False
            while p != p.parent:
                candidate = p / "config"
                if candidate.exists():
                    self.config_dir = candidate
                    found = True
                    break
                p = p.parent
            if not found:
                self.config_dir = Path("config")
        self._config_cache: Optional[AppConfig] = None
        self._last_reload = 0
    def load_yaml_config(self, environment: str) -> Dict[str, Any]:
        config_data = {}
        base_config_file = self.config_dir / "base.yaml"
        if base_config_file.exists():
            with open(base_config_file) as f:
                config_data = yaml.safe_load(f) or {}
        env_config_file = self.config_dir / f"{environment}.yaml"
        if env_config_file.exists():
            with open(env_config_file) as f:
                env_config = yaml.safe_load(f) or {}
                config_data = deep_merge(config_data, env_config)
        return config_data
    def load_config(self, force_reload: bool = False) -> AppConfig:
        if self._config_cache and not force_reload:
            return self._config_cache
        environment = os.getenv("ENVIRONMENT", "development").lower()
        yaml_config = self.load_yaml_config(environment)
        merged_config = self._merge_with_env(yaml_config)
        # Inject test defaults if missing required sections (for pytest/dev)
        if 'openai' not in merged_config:
            merged_config['openai'] = {
                'api_key': os.getenv('OPENAI_API_KEY', 'test'),
                'model': 'gpt-4o-mini',
                'max_tokens': 64,
                'temperature': 0.5,
            }
        if 'mcp' not in merged_config:
            merged_config['mcp'] = {
                'servers': [],
                'discovery_timeout': 5.0,
                'execution_timeout': 15.0,
                'health_check_interval': 30.0,
                'cache_ttl': 300.0,
                'max_retries': 1,
                'parallel_limit': 2,
            }
        if 'web' not in merged_config:
            merged_config['web'] = {
                'rate_limit': 1,
                'cache_ttl': 10,
                'max_content_length': 10000,
            }
        self._config_cache = AppConfig(**merged_config)
        return self._config_cache
    def _merge_with_env(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        return config_data
    def watch_for_changes(self, callback):
        pass
