# Alpha Token Monitor MVP

本项目用于本地监控 Binance Wallet / Binance Alpha 相关 Pre-TGE 代币线索。

## 功能

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
