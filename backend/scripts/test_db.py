import asyncio

from app.database import check_connection
from app import store


async def main() -> None:
    ok = await check_connection()
    print("database:", "up" if ok else "down")
    if not ok:
        return
    await store.init_db()
    await store.ensure_builtin_admin()
    await store.seed_categories_if_missing()
    print("categories:", await store.count_categories())


if __name__ == "__main__":
    asyncio.run(main())
