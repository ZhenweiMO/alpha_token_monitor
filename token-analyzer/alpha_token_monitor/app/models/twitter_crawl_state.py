from sqlalchemy import Column, Integer, String, DateTime, Boolean
from datetime import datetime

from app.db import Base


class TwitterCrawlState(Base):
    """记录每个Twitter账号的爬取状态"""
    __tablename__ = "twitter_crawl_states"

    id = Column(Integer, primary_key=True, index=True)
    account_name = Column(String, unique=True, index=True, nullable=False)
    last_tweet_id = Column(String, default="0")
    last_crawled_at = Column(DateTime, default=datetime.utcnow)
    total_crawled = Column(Integer, default=0)
    total_matched = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)

    def update_last_tweet(self, tweet_id: str):
        """更新最后爬取的推文ID"""
        self.last_tweet_id = tweet_id
        self.last_crawled_at = datetime.utcnow()
        self.total_crawled += 1

    def increment_matched(self):
        """匹配成功计数+1"""
        self.total_matched += 1