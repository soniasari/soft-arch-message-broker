from fastapi import FastAPI
from api.routes import router
from database.connection import engine
from database.models import Base

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Vehicle Tax Payment API",
    description="API for simulating vehicle tax payments",
    version="1.0.0"
)

app.include_router(router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)