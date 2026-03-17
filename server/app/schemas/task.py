from pydantic import BaseModel, Field


class StyleTransferRequest(BaseModel):
    style_id: int = Field(gt=0)
    input_image_url: str = Field(min_length=1, max_length=255)
