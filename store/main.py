import json
from typing import Set, Dict, List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Column,
    Integer,
    String,
    Float,
    DateTime,
)
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from pydantic import BaseModel, field_validator
from config import POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD

# ----------------------
# FastAPI app
# ----------------------
app = FastAPI()

# ----------------------
# Database setup
# ----------------------
DATABASE_URL = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
engine = create_engine(DATABASE_URL)
metadata = MetaData()

processed_agent_data = Table(
    "processed_agent_data",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("road_state", String, nullable=False),
    Column("user_id", Integer, nullable=False),
    Column("x", Float),
    Column("y", Float),
    Column("z", Float),
    Column("latitude", Float),
    Column("longitude", Float),
    Column("timestamp", DateTime),
)

SessionLocal = sessionmaker(bind=engine)

# ----------------------
# Pydantic models
# ----------------------
class AccelerometerData(BaseModel):
    x: float
    y: float
    z: float

class GpsData(BaseModel):
    latitude: float
    longitude: float

class AgentData(BaseModel):
    user_id: int
    accelerometer: AccelerometerData
    gps: GpsData
    timestamp: datetime

    @classmethod
    @field_validator("timestamp", mode="before")
    def check_timestamp(cls, value):
        if isinstance(value, datetime):
            return value
        try:
            return datetime.fromisoformat(value)
        except (TypeError, ValueError):
            raise ValueError(
                "Invalid timestamp format. Expected ISO 8601 format (YYYY-MM-DDTHH:MM:SS)."
            )

class ProcessedAgentData(BaseModel):
    road_state: str
    agent_data: AgentData

class ProcessedAgentDataInDB(BaseModel):
    id: int
    road_state: str
    user_id: int
    x: float
    y: float
    z: float
    latitude: float
    longitude: float
    timestamp: datetime

# ----------------------
# WebSocket subscriptions
# ----------------------
subscriptions: Dict[int, Set[WebSocket]] = {}

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await websocket.accept()
    if user_id not in subscriptions:
        subscriptions[user_id] = set()
    subscriptions[user_id].add(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        subscriptions[user_id].remove(websocket)

async def send_data_to_subscribers(user_id: int, data: dict):
    """Send data to all WebSocket clients subscribed for this user_id"""
    if user_id in subscriptions:
        for websocket in subscriptions[user_id]:
            await websocket.send_json(data)

# ----------------------
# CRUD endpoints
# ----------------------
@app.post("/processed_agent_data/")
async def create_processed_agent_data(data: List[ProcessedAgentData]):
    inserted = []
    with engine.begin() as conn:
        for item in data:
            query = processed_agent_data.insert().values(
                road_state=item.road_state,
                user_id=item.agent_data.user_id,
                x=item.agent_data.accelerometer.x,
                y=item.agent_data.accelerometer.y,
                z=item.agent_data.accelerometer.z,
                latitude=item.agent_data.gps.latitude,
                longitude=item.agent_data.gps.longitude,
                timestamp=item.agent_data.timestamp
            )
            result = conn.execute(query)
            inserted.append(result.inserted_primary_key[0])
    # Send WebSocket notifications
    for item in data:
        await send_data_to_subscribers(item.agent_data.user_id, {"new_data": True})
    return {"status": "ok", "inserted_ids": inserted}

@app.get("/processed_agent_data/{processed_agent_data_id}")
def read_processed_agent_data(processed_agent_data_id: int):
    with engine.connect() as conn:
        query = processed_agent_data.select().where(processed_agent_data.c.id == processed_agent_data_id)
        result = conn.execute(query).fetchone()
        if result:
            return dict(result._mapping)
        else:
            return {"error": "Not found"}

@app.get("/processed_agent_data/")
def list_processed_agent_data():
    with engine.connect() as conn:
        query = processed_agent_data.select()
        result = conn.execute(query).fetchall()
        return [dict(row._mapping) for row in result]

@app.put("/processed_agent_data/{processed_agent_data_id}")
def update_processed_agent_data(processed_agent_data_id: int, data: ProcessedAgentData):
    with engine.begin() as conn:
        query = processed_agent_data.update().where(
            processed_agent_data.c.id == processed_agent_data_id
        ).values(
            road_state=data.road_state,
            user_id=data.agent_data.user_id,
            x=data.agent_data.accelerometer.x,
            y=data.agent_data.accelerometer.y,
            z=data.agent_data.accelerometer.z,
            latitude=data.agent_data.gps.latitude,
            longitude=data.agent_data.gps.longitude,
            timestamp=data.agent_data.timestamp
        )
        conn.execute(query)
    return {"updated": processed_agent_data_id}

@app.delete("/processed_agent_data/{processed_agent_data_id}")
def delete_processed_agent_data(processed_agent_data_id: int):
    with engine.begin() as conn:
        query = processed_agent_data.delete().where(processed_agent_data.c.id == processed_agent_data_id)
        conn.execute(query)
    return {"deleted": processed_agent_data_id}

# ----------------------
# Run server
# ----------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)