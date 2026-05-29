from sqlalchemy import Column, BigInteger, Text, Boolean, Numeric, DateTime, JSON, UniqueConstraint, func

from app.db import Base


class SocialAnnouncement(Base):
 __tablename__ = "social_announcements"

 id = Column(BigInteger, primary_key=True, index=True)

 platform = Column(Text)
 account_name = Column(Text)
 account_id = Column(Text)
 account_type = Column(Text)

 post_id = Column(Text)
 post_url = Column(Text)
 content = Column(Text)

 published_at = Column(DateTime)
 detected_at = Column(DateTime, server_default=func.now())

 parsed_project_name = Column(Text)
 parsed_symbol = Column(Text)
 parsed_chain = Column(Text)
 parsed_contract_address = Column(Text)
 parsed_event_type = Column(Text)

 is_pre_tge = Column(Boolean, default=False)
 is_binance_wallet_related = Column(Boolean, default=False)
 is_binance_alpha_related = Column(Boolean, default=False)
 is_airdrop_related = Column(Boolean, default=False)
 is_tge_related = Column(Boolean, default=False)

 importance_score = Column(Numeric, default=0)
 confidence_score = Column(Numeric, default=0)

 raw_data = Column(JSON)

 __table_args__ = (
 UniqueConstraint("platform", "post_id", name="uq_social_post"),
 )
