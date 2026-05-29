from sqlalchemy import Column, BigInteger, Text, Boolean, Numeric, DateTime, JSON, func

from app.db import Base


class Alert(Base):
 __tablename__ = "alerts"

 id = Column(BigInteger, primary_key=True, index=True)

 project_id = Column(BigInteger)
 token_candidate_id = Column(BigInteger)
 signal_id = Column(BigInteger)

 alert_level = Column(Text)
 alert_type = Column(Text)

 title = Column(Text)
 message = Column(Text)

 score = Column(Numeric, default=0)

 is_sent = Column(Boolean, default=False)
 sent_channels = Column(JSON)

 created_at = Column(DateTime, server_default=func.now())
 sent_at = Column(DateTime)
