from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.MainRoute import router as main_router

app = FastAPI(title="Chemistry API", version="1.0.0")

# Configure CORS to accept requests from api.salsoftware.online
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://api.salsoftware.online",
        "http://api.salsoftware.online",
        "http://localhost:3000",  # For local development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the main router
app.include_router(main_router)

@app.get("/")
async def root():
    return {
        "message": "Chemistry API",
        "version": "1.0.0",
        "status": "active"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
