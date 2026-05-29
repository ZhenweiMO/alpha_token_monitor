import asyncio

from app.services.twitter_crawler import run_twitter_crawler


async def main():
    count = await run_twitter_crawler()
    print(f"Twitter crawler run completed, matched {count} valid announcements")


if __name__ == "__main__":
    asyncio.run(main())