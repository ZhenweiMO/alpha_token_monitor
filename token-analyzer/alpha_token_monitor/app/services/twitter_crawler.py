import re
import snscrape.modules.twitter as sntwitter
from sqlalchemy.orm import Session
from datetime import datetime

from app.config import settings
from app.models.twitter_crawl_state import TwitterCrawlState
from app.api.announcements import create_announcement, AnnouncementCreate
from app.db import get_db


def get_match_keywords() -> list:
    """获取匹配关键词列表"""
    return [k.strip().lower() for k in settings.twitter_match_keywords.split(",") if k.strip()]


def get_exclude_keywords() -> list:
    """获取排除关键词列表"""
    return [k.strip().lower() for k in settings.twitter_exclude_keywords.split(",") if k.strip()]


def get_crawl_accounts() -> list:
    """获取要爬取的账号列表"""
    return [a.strip() for a in settings.twitter_crawl_accounts.split(",") if a.strip()]


def get_or_create_crawl_state(db: Session, account_name: str) -> TwitterCrawlState:
    """获取或创建账号的爬取状态"""
    state = db.query(TwitterCrawlState).filter(TwitterCrawlState.account_name == account_name).first()
    if not state:
        state = TwitterCrawlState(
            account_name=account_name,
            last_tweet_id="0"
        )
        db.add(state)
        db.commit()
        db.refresh(state)
    return state


async def crawl_twitter_account(account_name: str, db: Session) -> int:
    """爬取单个Twitter账号的最新推文
    :return: 匹配到的有效推文数量
    """
    match_count = 0
    match_keywords = get_match_keywords()
    exclude_keywords = get_exclude_keywords()
    limit = settings.twitter_crawl_limit_per_run

    state = get_or_create_crawl_state(db, account_name)
    last_tweet_id = int(state.last_tweet_id) if state.last_tweet_id.isdigit() else 0

    try:
        # 构建爬取查询：从指定账号爬取，并且比last_tweet_id新的推文
        query = f"from:{account_name}"
        if last_tweet_id > 0:
            query += f" since_id:{last_tweet_id}"

        # 爬取推文
        tweets = []
        for i, tweet in enumerate(sntwitter.TwitterSearchScraper(query).get_items()):
            if i >= limit:
                break
            tweets.append(tweet)

        if not tweets:
            return 0

        # 处理推文，从新到旧，更新最大tweet_id
        max_tweet_id = last_tweet_id
        for tweet in reversed(tweets):
            tweet_id = tweet.id
            if tweet_id > max_tweet_id:
                max_tweet_id = tweet_id

            # 排除转发、回复
            if tweet.retweetedTweet or tweet.inReplyToUserId:
                continue

            content = tweet.rawContent
            lower_content = content.lower()

            # 匹配关键词
            has_match = any(k in lower_content for k in match_keywords)
            if not has_match:
                continue

            # 排除关键词
            has_exclude = any(k in lower_content for k in exclude_keywords)
            if has_exclude:
                continue

            # 构造公告payload，调用现有接口创建
            payload = AnnouncementCreate(
                platform="twitter",
                account_name=account_name,
                account_type="official",
                post_id=str(tweet_id),
                post_url=f"https://twitter.com/{account_name}/status/{tweet_id}",
                content=content
            )

            # 调用现有创建接口，复用全部逻辑
            result = await create_announcement(payload, db)
            if not result.get("duplicate"):
                match_count += 1
                state.increment_matched()

        # 更新最后爬取ID
        if max_tweet_id > last_tweet_id:
            state.last_tweet_id = str(max_tweet_id)
            state.last_crawled_at = datetime.utcnow()
            db.commit()

        return match_count

    except Exception as e:
        print(f"[ERROR] 爬取Twitter账号 {account_name} 失败: {str(e)}")
        return 0


async def run_twitter_crawler() -> int:
    """运行全量Twitter爬虫任务
    :return: 总匹配到的有效推文数量
    """
    if not settings.twitter_crawler_enabled:
        return 0

    total_matched = 0
    accounts = get_crawl_accounts()
    if not accounts:
        return 0

    # 获取数据库会话
    db = next(get_db())
    try:
        for account in accounts:
            count = await crawl_twitter_account(account, db)
            total_matched += count
            print(f"[INFO] 爬取Twitter账号 {account} 完成，匹配到 {count} 条有效推文")
    finally:
        db.close()

    return total_matched