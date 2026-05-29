from sqlalchemy import Column, BigInteger, Text, Numeric, DateTime, JSON, func

from app.db import Base


class PreTgeSignal(Base):
 __tablename__ = "pre_tge_signals"

 id = Column(BigInteger, primary_key=True, index=True)

 project_id = Column(BigInteger)
 token_candidate_id = Column(BigInteger)

 signal_type = Column(Text)
 signal_source = Column(Text)

 signal_time = Column(DateTime)
 detected_at = Column(DateTime, server_default=func.now())

 title = Column(Text)
 description = Column(Text)
 source_url = Column(Text)

 importance_score = Column(Numeric, default=0)
 confidence_score = Column(Numeric, default=0)

 raw_data = Column(JSON)
