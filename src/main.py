"""Main application entry point."""
from fastapi import FastAPI
from nicegui import ui
from src.config import settings

# Import UI pages
from src.ui.pages.home import create_home_page
from src.ui.pages.users_with_soft_delete import create_users_page
from src.ui.pages.leads import create_leads_page

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="A unified FastAPI + NiceGUI application",
    debug=settings.DEBUG
)


@app.get("/health")
def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "ok", "service": "SinaptrixTwo"}


def init_nicegui():
    """Initialize NiceGUI and register all pages."""
    # Register all UI pages
    create_home_page()
    create_leads_page()
    create_users_page()
    
    # Mount NiceGUI to FastAPI
    ui.run_with(
        app,
        title=settings.APP_NAME,
        storage_secret=settings.STORAGE_SECRET
    )

init_nicegui()

if __name__ == "__main__":
    import uvicorn
    # Reload is enabled for development convenience
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
