from typing import List
from fastapi import FastAPI, Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from contextlib import asynccontextmanager

from app.database import engine, Base, get_db, Area
from app.producer import kafka_producer
from app.areatype import AreaType
from app.schemas import *

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all);

    await kafka_producer.start();
    yield;
    await kafka_producer.stop();

app = FastAPI(lifespan=lifespan);

@app.get("/health")
async def health():
    return {"status": "ok"};

@app.post("/areas", response_model=AreaResponse)
async def create_area(
    area_data: AreaCreate,
    x_user_role: str = Header(None),
    db: AsyncSession = Depends(get_db),
):
    if (
        area_data.area_type == AreaType.NADLESNICTWO
        and x_user_role != "Dyrektor"
    ):
        raise HTTPException(
            status_code=403, detail="Only a director can create overforestries"
        );

    if area_data.area_type == AreaType.LESNICTWO and x_user_role not in [
        "Nadlesniczy",
        "Dyrektor",
    ]:
        raise HTTPException(
            status_code=403, detail="Permission denied"
        );

    new_area = Area(
        name=area_data.name,
        area_type=area_data.area_type.value,
        parent_area_id=area_data.parent_area_id,
    );
    db.add(new_area);
    await db.commit();
    await db.refresh(new_area);

    await kafka_producer.send_event(
        event_type="AreaCreated",
        payload={
            "id": new_area.id,
            "name": new_area.name,
            "type": new_area.area_type,
        },
    );
    return new_area;


@app.delete("/areas/{area_id}")
async def delete_area(
    area_id: int,
    x_user_role: str = Header(None),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Area).where(Area.id == area_id);
    result = await db.execute(stmt);
    area = result.scalar_one_or_none();

    if not area:
        raise HTTPException(status_code=404, detail="Area does not exist");

    if area.area_type == AreaType.NADLESNICTWO.value and x_user_role != "Dyrektor":
        raise HTTPException(
            status_code=403, detail="Only a Director can delete overforestries"
        );
    if area.area_type == AreaType.LESNICTWO.value and x_user_role not in [
        "Nadleśniczy",
        "Dyrektor",
    ]:
        raise HTTPException(
            status_code=403, detail="Permission denied"
        );

    await db.delete(area);
    await db.commit();

    await kafka_producer.send_event(
        event_type="AreaDeleted", payload={"id": area_id}
    );
    return {"status": "usunięto", "id": area_id};


@app.get("/areas/hierarchy", response_model=List[AreaHierarchyResponse])
async def get_areas_hierarchy(db: AsyncSession = Depends(get_db)):
    stmt = (
        select(Area)
        .where(Area.parent_area_id == None)
        .options(selectinload(Area.subareas))
    );
    result = await db.execute(stmt);
    return result.scalars().all();
