from pydantic import BaseModel

class Results(BaseModel):
    status: str
    message: str
    min_age: int
    max_age: int
    avg_age: float