import re


def extract_symbol(content: str) -> str | None:
    dollar_symbols = re.findall(r"\$([A-Za-z0-9]{2,20})", content)
    if dollar_symbols:
        return dollar_symbols[0].upper()

    # 常见写法：Token: ABC / Symbol: ABC
    patterns = [
        r"symbol[:：]\s*([A-Za-z0-9]{2,20})",
        r"token[:：]\s*([A-Za-z0-9]{2,20})",
    ]

    for pattern in patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            return match.group(1).upper()

    return None


def extract_contract(content: str) -> str | None:
    match = re.search(r"0x[a-fA-F0-9]{40}", content)
    if match:
        return match.group(0).lower()
    return None


def parse_social_content(content: str) -> dict:
    lower = content.lower()

    is_binance_wallet_related = (
        "binance wallet" in lower
        or "binance web3 wallet" in lower
        or "binance web3" in lower
    )

    is_binance_alpha_related = (
        "binance alpha" in lower
        or "alpha" in lower
    )

    is_airdrop_related = (
        "airdrop" in lower
        or "claim" in lower
        or "rewards" in lower
        or "reward" in lower
        or "空投" in content
        or "领取" in content
    )

    is_tge_related = (
        "tge" in lower
        or "token generation event" in lower
        or "launch" in lower
        or "上线" in content
        or "代币生成" in content
    )

    is_pre_tge = (
        is_tge_related
        or is_airdrop_related
        or "coming soon" in lower
        or "soon" in lower
        or "upcoming" in lower
        or "即将" in content
    )

    parsed_symbol = extract_symbol(content)
    parsed_contract = extract_contract(content)

    score = 0

    if is_binance_wallet_related:
        score += 30

    if is_binance_alpha_related:
        score += 25

    if is_airdrop_related:
        score += 15

    if is_tge_related:
        score += 15

    if parsed_symbol:
        score += 10

    if parsed_contract:
        score += 20

    if is_binance_wallet_related and is_airdrop_related:
        event_type = "binance_wallet_airdrop_notice"
    elif is_binance_wallet_related and is_tge_related:
        event_type = "binance_wallet_tge_notice"
    elif is_binance_alpha_related:
        event_type = "binance_alpha_hint"
    elif parsed_contract:
        event_type = "official_contract_mentioned"
    else:
        event_type = "social_announcement"

    return {
        "parsed_project_name": parsed_symbol,
        "parsed_symbol": parsed_symbol,
        "parsed_chain": "bsc" if "bsc" in lower or "bnb chain" in lower or "bep20" in lower else None,
        "parsed_contract_address": parsed_contract,
        "parsed_event_type": event_type,
        "is_pre_tge": is_pre_tge,
        "is_binance_wallet_related": is_binance_wallet_related,
        "is_binance_alpha_related": is_binance_alpha_related,
        "is_airdrop_related": is_airdrop_related,
        "is_tge_related": is_tge_related,
        "importance_score": min(100, score),
        "confidence_score": min(100, score),
    }
