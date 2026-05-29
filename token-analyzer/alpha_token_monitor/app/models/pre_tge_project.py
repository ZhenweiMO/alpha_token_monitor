from sqlalchemy import Column, BigInteger, Text, Boolean, Numeric, DateTime, func

from app.db import Base


class PreTgeProject(Base):
 __tablename__ = "pre_tge_projects"

 id = Column(BigInteger, primary_key=True, index=True)

 project_name = Column(Text)
 expected_symbol = Column(Text)
 chain = Column(Text, default="bsc")
 status = Column(Text, default="pre_tge_candidate")

 official_website = Column(Text)
 twitter_url = Column(Text)
 telegram_url = Column(Text)
 discord_url = Column(Text)
 docs_url = Column(Text)

 binance_wallet_related = Column(Boolean, default=False)
 binance_alpha_related = Column(Boolean, default=False)
 bnb_chain_related = Column(Boolean, default=False)

 tge_announced = Column(Boolean, default=False)
 expected_tge_time = Column(DateTime)
 confirmed_tge_time = Column(DateTime)

 confidence_score = Column(Numeric, default=0)
 importance_score = Column(Numeric, default=0)
 risk_score = Column(Numeric, default=0)

 source = Column(Text)
 source_url = Column(Text)

 first_seen_at = Column(DateTime, server_default=func.now())
 updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
