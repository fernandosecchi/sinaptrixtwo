"""Application initialization and startup."""
import uvicorn
from src.main import app, init_nicegui
from src.config import settings


def run():
    """Run the application."""
    # Initialize NiceGUI pages
    init_nicegui()
    
    # Run with Uvicorn
    uvicorn.run(
        "src.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        log_level="debug" if settings.DEBUG else "info"
    )


if __name__ == "__main__":
    run()