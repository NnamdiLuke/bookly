from sqlmodel import create_engine, text,SQLModel
# from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio import create_async_engine
from src.config import Config
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker
from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import async_sessionmaker



# engine = AsyncEngine(
#     create_engine(
#         url=Config.DATABASE_URL,
#         echo=True
#     )
# )

engine = create_async_engine(
    Config.DATABASE_URL,
    echo=True
)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


# async def get_session() -> AsyncSession:
#     Session = sessionmaker(
#         bind=engine, 
#         class_=AsyncSession, 
#         expire_on_commit=False
#     )
#     async with Session as session:
#         yield session

SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session
