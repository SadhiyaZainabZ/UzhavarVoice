from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=10000)
    stream: bool = False


class ChatResponse(BaseModel):
    answer: str
    model: str
    input_tokens: int
    output_tokens: int
    estimated_cost_usd: float
    fallback_used: bool
