import asyncio

from app.db import SessionLocal
from app.services.bsc_transfer_watcher import scan_all_watch_addresses


async def main():
    db = SessionLocal()
    try:
        count = await scan_all_watch_addresses(db)
        print(f"new transfers inserted: {count}")
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())
