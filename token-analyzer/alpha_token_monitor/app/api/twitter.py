from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.twitter_crawl_state import TwitterCrawlState
from app.services.twitter_crawler import run_twitter_crawler


router = APIRouter(prefix="/twitter", tags=["twitter"])


@router.post("/crawl", description="手动触发Twitter爬虫任务")
async def manual_crawl():
    count = await run_twitter_crawler()
    return {
        "status": "success",
        "message": f"Twitter爬虫运行完成，匹配到 {count} 条有效活动公告"
    }


@router.get("/states", description="获取所有Twitter账号的爬取状态")
def get_crawl_states(db: Session = Depends(get_db)):
    states = db.query(TwitterCrawlState).order_by(TwitterCrawlState.account_name).all()
    return {
        "status": "success",
        "data": states
    }