from sqlalchemy import Column, BigInteger, Text, Boolean, Numeric, DateTime, UniqueConstraint, func

from app.db import Base


class ProjectTokenCandidate(Base):
 __tablename__ = "project_token_candidates"

 id = Column(BigInteger, primary_key=True, index=True)

 project_id = Column(BigInteger)

 chain = Column(Text, nullable=False, default="bsc")
 contract_address = Column(Text, nullable=False)

 symbol = Column(Text)
 name = Column(Text)
 decimals = Column(BigInteger)
 total_supply = Column(Numeric)

 candidate_type = Column(Text)
 confidence_score = Column(Numeric, default=0)
 risk_score = Column(Numeric, default=0)

 is_verified_contract = Column(Boolean)
 is_proxy = Column(Boolean)
 owner_address = Column(Text)
 deployer_address = Column(Text)
 deployed_at = Column(DateTime)

 source = Column(Text)
 source_url = Column(Text)

 first_seen_at = Column(DateTime, server_default=func.now())
 updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

 __table_args__ = (
 UniqueConstraint("chain", "contract_address", name="uq_candidate_chain_contract"),
 )
