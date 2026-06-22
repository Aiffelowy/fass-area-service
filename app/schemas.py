from app.areatype import AreaType
from pydantic import BaseModel, ConfigDict
from typing import List, Optional

class AreaCreate(BaseModel):
    name: str;
    area_type: AreaType;
    parent_area_id: Optional[int] = None;


class AreaResponse(BaseModel):
    id: int;
    name: str;
    area_type: AreaType;
    parent_area_id: Optional[int] = None;

    model_config = ConfigDict(from_attributes=True);


class AreaHierarchyResponse(AreaResponse):
    subareas: List["AreaHierarchyResponse"] = [];
