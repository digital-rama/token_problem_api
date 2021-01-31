from sqlalchemy import Boolean, Column, ForeignKey, Numeric, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import true
from sqlalchemy.sql.functions import func
import datetime
from db_conf import Base


class Token(Base):
    __tablename__ = "token_table"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True),
                        default=datetime.datetime.now())
    token_name = Column(String, unique=True, index=True)
    is_assigned = Column(Boolean, default=False)
    assign_at = Column(DateTime(timezone=True))
