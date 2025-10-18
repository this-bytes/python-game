"""Backend configuration settings."""
import os
from dotenv import load_dotenv

load_dotenv()


class BackendConfig:
    """Configuration for the backend API server."""
    
    # Server settings
    HOST = os.getenv("BACKEND_HOST", "0.0.0.0")
    PORT = int(os.getenv("BACKEND_PORT", "5001"))
    DEBUG = os.getenv("BACKEND_DEBUG", "True").lower() == "true"
    
    # CORS settings
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")
    
    # Game integration
    ENABLE_BACKEND = os.getenv("ENABLE_BACKEND", "False").lower() == "true"
    
    # WebSocket settings
    WEBSOCKET_PING_INTERVAL = 25
    WEBSOCKET_PING_TIMEOUT = 60
    
    # API settings
    API_PREFIX = "/api"
    
    @classmethod
    def to_dict(cls):
        """Convert config to dictionary."""
        return {
            "host": cls.HOST,
            "port": cls.PORT,
            "debug": cls.DEBUG,
            "cors_origins": cls.CORS_ORIGINS,
            "enable_backend": cls.ENABLE_BACKEND,
            "api_prefix": cls.API_PREFIX
        }
