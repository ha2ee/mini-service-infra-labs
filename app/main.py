import asyncio
import os

from fastapi import FastAPI, HTTPException

app = FastAPI(
    title="Mini Service Infra Lab App",
    description="Infra and ops practice app for health checks, failure simulation, and request flow testing",
    version="0.1.0",
)


@app.get("/")
def read_root():
    return {
        "service": "mini-service-infra-lab",
        "message": "app is running",
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "message": "process is alive",
    }


@app.get("/ready")
def readiness_check():
    lab_env = os.getenv("LAB_ENV")
    if not lab_env:
        raise HTTPException(status_code=503, detail="LAB_ENV is not set")

    return {
        "status": "ready",
        "message": "app is ready to serve traffic",
        "lab_env": lab_env,
    }


@app.get("/slow")
async def slow_response():
    await asyncio.sleep(3)
    return {
        "status": "delayed",
        "delay_seconds": 3,
    }


@app.get("/error")
def error_response():
    raise HTTPException(status_code=500, detail="intentional error for lab")
