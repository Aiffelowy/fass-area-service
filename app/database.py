from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy import Enum as SQLEnum
from app.config import settings
from app.areatype import AreaType

engine = create_async_engine(settings.DATABASE_URL, echo=True);
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False);
Base = declarative_base();

class Area(Base):
    __tablename__ = "areas";

    id = Column(Integer, primary_key=True, index=True);
    name = Column(SQLEnum(AreaType), unique=True, index=True, nullable=False);
    area_type = Column(
        String, nullable=False
    );

    parent_area_id = Column(
        Integer, ForeignKey("areas.id", ondelete="CASCADE"), nullable=True
    );

    parent = relationship("Area", remote_side=[id], backref="subareas");


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session;
