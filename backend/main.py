from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from backend.core.database import init_db
from backend.api.endpoints import auth, tickets, monitor

app = FastAPI(title="Ticket System API")

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for development, restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    await init_db()

# Include Routers
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(tickets.router, prefix="/api/tickets", tags=["Tickets"])

@app.websocket("/ws/monitor")
async def websocket_monitor(websocket: WebSocket):
    await monitor.manager.connect(websocket)
    try:
        while True:
            # We don't expect the client to send messages, just keep it alive
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        monitor.manager.disconnect(websocket)
