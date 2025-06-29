from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncEngine


class DatabaseEngine:
    def __init__(self, host: str, **engine_kwargs):
        self._engine: AsyncEngine = create_async_engine(url=host, **engine_kwargs)
        self._sessionmaker: async_sessionmaker = async_sessionmaker(
            expire_on_commit=False, bind=self._engine
        )

    async def __aenter__(self) -> "DatabaseEngine":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        # Dispose the engine to properly close pooled connections
        await self._engine.dispose()
