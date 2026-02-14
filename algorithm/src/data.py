from pydantic import BaseModel


class InputParameters(BaseModel):
    num: int
    age: int