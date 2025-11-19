from fastapi import FastAPI
from nicegui import ui

# Initialize FastAPI app
app = FastAPI(title="SinaptrixTwo", version="0.1.0")

@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok"}

# NiceGUI setup
def init_nicegui():
    @ui.page("/")
    def main_page():
        with ui.column().classes("w-full items-center justify-center min-h-screen bg-slate-100"):
            with ui.card().classes("p-8 shadow-xl rounded-lg"):
                ui.label("SinaptrixTwo").classes("text-4xl font-bold text-slate-800 mb-4")
                ui.label("FastAPI + NiceGUI + PostgreSQL").classes("text-xl text-slate-600")
                ui.button("Click me!", on_click=lambda: ui.notify("Hello from NiceGUI!")).classes("mt-6 bg-blue-500 text-white")

    # Mount NiceGUI to FastAPI
    # storage_secret must be set for sessions to work
    ui.run_with(app, title="SinaptrixTwo", storage_secret="change-this-secret-in-production")

init_nicegui()

if __name__ == "__main__":
    import uvicorn
    # Reload is enabled for development convenience
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
