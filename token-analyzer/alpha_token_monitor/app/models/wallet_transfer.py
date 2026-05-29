from sqlalchemy import Column, BigInteger, Text, Boolean, Numeric, DateTime, UniqueConstraint, func

from app.db import Base


class WatchedAddressTokenTransfer(Base):
 __tablename__ = "watched_address_token_transfers"

 id = Column(BigInteger, primary_key=True, index=True)

 chain = Column(Text, nullable=False, default="bsc")
 tx_hash = Column(Text, nullable=False)
 block_number = Column(BigInteger)
 block_time = Column(DateTime)

 watched_address = Column(Text, nullable=False)
 direction = Column(Text)

 token_contract = Column(Text, nullable=False)
 token_symbol = Column(Text)
 token_name = Column(Text)
 token_decimals = Column(BigInteger)

 from_address = Column(Text)
 to_address = Column(Text)

 amount_raw = Column(Numeric)
 amount_decimal = Column(Numeric)

 token_total_supply = Column(Numeric)
 amount_supply_ratio = Column(Numeric)

 is_new_token = Column(Boolean, default=False)
 is_first_seen_for_address = Column(Boolean, default=False)

 created_at = Column(DateTime, server_default=func.now())

 __table_args__ = (
 UniqueConstraint(
 "chain",
 "tx_hash",
 "watched_address",
 "token_contract",
 name="uq_watched_transfer",
 ),
 )
