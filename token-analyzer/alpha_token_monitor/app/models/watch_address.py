from sqlalchemy import Column, BigInteger, Text, Boolean, Numeric, DateTime, UniqueConstraint, func

from app.db import Base


class WatchAddress(Base):
 __tablename__ = "watch_addresses"

 id = Column(BigInteger, primary_key=True, index=True)

 chain = Column(Text, nullable=False, default="bsc")
 address = Column(Text, nullable=False)

 label = Column(Text)
 label_type = Column(Text)

 confidence_score = Column(Numeric, default=0)
 evidence = Column(Text)
 source_url = Column(Text)

 is_active = Column(Boolean, default=True)

 first_seen_at = Column(DateTime, server_default=func.now())
 last_checked_at = Column(DateTime)
 updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

 __table_args__ = (
 UniqueConstraint("chain", "address", name="uq_watch_address_chain_address"),
 )
