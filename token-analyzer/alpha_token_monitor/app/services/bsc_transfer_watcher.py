import datetime
from decimal import Decimal

import httpx
from sqlalchemy import func

from app.config import settings
from app.db import SessionLocal  # 虽然由外部传入，但保留导入以防万一
from app.models.watch_address import WatchAddress
from app.models.wallet_transfer import WatchedAddressTokenTransfer

MORALIS_API_URL = "https://deep-index.moralis.io/api/v2.2"


async def fetch_bep20_transfers(address: str, startblock: int = 0):
    """底层 API 请求函数：调用 Moralis 获取转账记录"""
    if not settings.moralis_api_key:
        raise RuntimeError("MORALIS_API_KEY is missing in .env")

    url = f"{MORALIS_API_URL}/{address}/erc20/transfers"

    params = {
        "chain": "bsc",
        "from_block": startblock,
        "limit": 100,
    }

    headers = {
        "Accept": "application/json",
        "X-API-Key": settings.moralis_api_key,
    }

    client_kwargs = {"timeout": 30}
    if settings.outbound_proxy:
        # httpx >= 0.24.0 使用 proxy 替代了 proxies
        client_kwargs["proxy"] = settings.outbound_proxy

    async with httpx.AsyncClient(**client_kwargs) as client:
        try:
            resp = await client.get(url, params=params, headers=headers)
            resp.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise RuntimeError(
                f"Moralis API request failed with status {e.response.status_code}. "
                f"Response: {e.response.text[:200]}"
            ) from None
        except httpx.RequestError as e:
            raise RuntimeError(f"Moralis API connection error: {type(e).__name__}") from None

        data = resp.json()

    result = data.get("result", [])
    if not result:
        return []

    mapped_result = []
    for item in result:
        # 转换时间戳格式 (Moralis 是 ISO 格式，BscScan 是 Unix 时间戳字符串)
        ts = item.get("block_timestamp", "")
        if ts:
            try:
                dt = datetime.datetime.fromisoformat(ts.replace('Z', '+00:00'))
                ts = str(int(dt.timestamp()))
            except Exception:
                pass

        mapped_result.append({
            "hash": item.get("transaction_hash"),
            "blockNumber": item.get("block_number"),
            "timeStamp": ts,
            "from": item.get("from_address"),
            "to": item.get("to_address"),
            "contractAddress": item.get("address"),
            "value": item.get("value"),
            "tokenName": item.get("token_name", ""),
            "tokenSymbol": item.get("token_symbol", ""),
            "tokenDecimal": item.get("token_decimals", ""),
        })

    return mapped_result


async def scan_all_watch_addresses(db):
    """
    扫描所有监控地址的 BEP20 转账记录
    :param db: SQLAlchemy 同步会话
    :return: 新插入的记录数
    """
    total_inserted = 0

    # 1. 获取所有活跃的监控地址
    watch_addresses = db.query(WatchAddress).filter(WatchAddress.is_active == True).all()

    for wa in watch_addresses:
        address = wa.address

        # 2. 智能获取 startblock：从数据库查该地址最大的 block_number
        max_block = db.query(func.max(WatchedAddressTokenTransfer.block_number))\
            .filter(WatchedAddressTokenTransfer.watched_address == address)\
            .scalar()

        # 如果数据库里有记录，从最大区块号开始扫（包含该区块，防止漏扫同一区块的后续交易）；否则从 0 开始
        start_block = max_block if max_block else 0

        try:
            # 3. 调用 Moralis API
            transfers = await fetch_bep20_transfers(address, startblock=start_block)
        except Exception as e:
            print(f"[ERROR] 扫描地址 {address} 出错: {e}")
            continue

        if not transfers:
            continue

        # 4. 查询已存在的记录，防止重复插入 (利用唯一约束字段)
        tx_hashes = [t["hash"] for t in transfers]
        existing_records = db.query(
            WatchedAddressTokenTransfer.tx_hash,
            WatchedAddressTokenTransfer.token_contract
        ).filter(
            WatchedAddressTokenTransfer.watched_address == address,
            WatchedAddressTokenTransfer.tx_hash.in_(tx_hashes)
        ).all()

        # 将已存在的记录放入集合中，查找时速度极快
        existing_set = set((r.tx_hash, r.token_contract) for r in existing_records)

        # 5. 映射数据并过滤
        new_transfers = []
        for t in transfers:
            # 去重判断
            if (t["hash"], t["contractAddress"]) in existing_set:
                continue

            # 判断方向 (忽略大小写比较)
            direction = "in" if t["to"].lower() == address.lower() else "out"

            # 时间戳转换
            block_time = None
            if t.get("timeStamp"):
                try:
                    block_time = datetime.datetime.fromtimestamp(int(t["timeStamp"]))
                except:
                    pass

            # 精度处理 (安全计算 amount_decimal)
            decimals = int(t.get("tokenDecimal") or 0)
            amount_raw = t.get("value", "0")
            try:
                # Decimal 防止浮点数精度丢失
                amount_decimal = Decimal(str(amount_raw)) / (Decimal("10") ** decimals) if decimals > 0 else Decimal("0")
            except:
                amount_decimal = Decimal("0")

            transfer_obj = WatchedAddressTokenTransfer(
                chain="bsc",
                tx_hash=t["hash"],
                block_number=int(t.get("blockNumber", 0)),
                block_time=block_time,
                watched_address=address,
                direction=direction,
                token_contract=t.get("contractAddress", ""),
                token_symbol=t.get("tokenSymbol", ""),
                token_name=t.get("tokenName", ""),
                token_decimals=decimals,
                from_address=t.get("from"),
                to_address=t.get("to"),
                amount_raw=amount_raw,
                amount_decimal=amount_decimal,
            )
            new_transfers.append(transfer_obj)

        # 6. 批量插入新记录
        if new_transfers:
            db.add_all(new_transfers)
            db.commit()
            total_inserted += len(new_transfers)

        # 7. 更新该地址的最后检查时间
        wa.last_checked_at = datetime.datetime.now()
        db.commit()

    return total_inserted
