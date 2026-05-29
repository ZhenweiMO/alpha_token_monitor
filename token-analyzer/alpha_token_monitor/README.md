# Alpha Token Monitor
本项目用于本地监控 Binance Wallet / Binance Alpha 相关 Pre-TGE 代币线索。
## 版本更新
### v0.2.0 (2026-05-29)
✅ 新增自动Twitter爬虫功能
- 支持自动爬取指定Twitter账号（默认binance_wallet）的最新推文
- 自动匹配识别：空投(airdrop/空投)、TGE、Pre-TGE、Booster 4类活动
- 完全复用现有解析、生成项目、生成信号、Telegram推送全链路
- 增量爬取，自动记录最后爬取ID，不会重复处理、不会重复告警
- 支持定时自动运行，默认15分钟一次，可配置
- 支持手动触发爬虫API
- 支持爬取状态查询API
### v0.1.0 (2026-05-xx)
✅ 基础MVP功能全通
- 维护 BSC 监听地址
- 手动导入 Binance Wallet / Alpha 推文或公告
- 自动解析 Pre-TGE / Alpha / Airdrop / TGE 关键词
- 自动生成 Pre-TGE 项目和信号
- 扫描监听地址 BEP-20 Transfer
- 首次收到新 Token 时生成信号和告警
- 可选 Telegram 推送
## 启动
```bash
docker compose up -d
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# 填写.env里的配置项，包括可选的Twitter相关配置
uvicorn app.main:app --reload
```
访问：
```text
http://127.0.0.1:8000/docs
```
## 手动扫描 BSC 钱包
```bash
python -m app.tasks.run_bsc_watcher
```
## 手动运行Twitter爬虫
```bash
python -m app.tasks.run_twitter_crawler
```
## Twitter爬虫配置（在.env中设置）
```env
# Twitter爬虫开关
TWITTER_CRAWLER_ENABLED=true
# 爬取间隔（分钟，推荐15分钟，不会触发限流）
TWITTER_CRAWL_INTERVAL=15
# 要爬的账号列表，逗号分隔
TWITTER_CRAWL_ACCOUNTS="binance_wallet"
# 每次爬取最新N条推文（推荐10条，足够覆盖15分钟内的更新）
TWITTER_CRAWL_LIMIT_PER_RUN=10
# 匹配关键词，逗号分隔
TWITTER_MATCH_KEYWORDS="airdrop,空投,tge,pre-tge,booster"
# 排除关键词（可选，过滤掉测试/无关内容）
TWITTER_EXCLUDE_KEYWORDS="test,fake,scam"
```
## API接口
### Twitter相关
- `POST /twitter/crawl`：手动触发Twitter爬虫
- `GET /twitter/states`：获取所有Twitter账号的爬取状态
### 其他基础接口
- `/watch-addresses`：地址CRUD
- `/announcements`：公告导入、查询
- `/projects`：项目查询
- `/signals`：信号查询
- `/transfers`：转账记录查询
- `/alerts`：告警查询
- `/health`：健康检查