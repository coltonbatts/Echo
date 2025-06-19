from pydantic_settings import BaseSettings
from pydantic import Field, field_validator, ConfigDict
from typing import List, Optional, Dict, Any
from enum import Enum

class Environment(str, Enum):
    LOCAL = "local"
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class OpenAIConfig(BaseSettings):
    api_key: str = Field(..., description="OpenAI API key")
    model: str = Field("gpt-4o-mini", description="Default OpenAI model")
    max_tokens: int = Field(512, ge=1, le=4096)
    temperature: float = Field(0.7, ge=0.0, le=2.0)
    
    model_config = ConfigDict(env_prefix="OPENAI_")

class MCPServerConfig(BaseSettings):
    url: str
    name: str
    timeout: float = Field(10.0, ge=1.0)
    retries: int = Field(3, ge=0)
    enabled: bool = True

class MCPConfig(BaseSettings):
    servers: List[MCPServerConfig] = Field(default_factory=list)
    discovery_timeout: float = Field(5.0, ge=1.0)
    execution_timeout: float = Field(15.0, ge=1.0)
    health_check_interval: float = Field(30.0, ge=5.0)
    cache_ttl: float = Field(300.0, ge=0.0)
    max_retries: int = Field(3, ge=0)
    parallel_limit: int = Field(10, ge=1)
    
    @field_validator('servers', mode='before')
    def parse_servers(cls, v):
        if isinstance(v, str):
            urls = v.split(',')
            return [
                MCPServerConfig(
                    url=url.strip(),
                    name=f"server_{i}"
                ) for i, url in enumerate(urls)
            ]
        return v
    
    model_config = ConfigDict(env_prefix="MCP_")

class WebServerConfig(BaseSettings):
    search_api_key: Optional[str] = None
    rate_limit: int = Field(10, ge=1)
    cache_ttl: int = Field(300, ge=0)
    max_content_length: int = Field(50000, ge=1000)
    
    model_config = ConfigDict(env_prefix="WEB_")

class AppConfig(BaseSettings):
    app_name: str = "Echo"
    app_version: str = "1.1.0"
    environment: Environment = Environment.DEVELOPMENT
    debug: bool = False
    log_level: LogLevel = LogLevel.INFO
    use_intelligent_selection: bool = True
    enable_metrics: bool = False
    enable_tracing: bool = False
    openai: OpenAIConfig
    mcp: MCPConfig
    web: WebServerConfig
    claude_api_key: Optional[str] = None
    ollama_endpoint: Optional[str] = None
    
    @field_validator('environment', mode='before')
    def validate_environment(cls, v):
        if isinstance(v, str):
            return Environment(v.lower())
        return v
    
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

# Placeholder for custom YAML loader if needed by loader.py
