from typing import Optional

import pydantic


class CreateAdv(pydantic.BaseModel):
    header: str
    description: str
    owner: str


class UpdateAdv(pydantic.BaseModel):
    header: Optional[str] = None
    description: Optional[str] = None
    owner: Optional[str] = None
