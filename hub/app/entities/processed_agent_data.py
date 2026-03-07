from pydantic import BaseModel


class ProcessedAgentData(BaseModel):
    road_state: str
