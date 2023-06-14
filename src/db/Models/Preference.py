from sqlalchemy import Column, Float, Integer, String
from src.db import Database

class Preference(Database.Base):
    """
    Model: Preference
    Voicevox preference data
    user_id     :Discord UserID
    server_id   :Discord ServerID
    speaker       :Voicevox Speaker(default: ずんだもん/ノーマル)
    
    """
    __tablename__ = "preferences"
    user_id     = Column("user_id", String(32), nullable=False, primary_key=True)
    server_id   = Column("server_id", String(32), nullable=False, primary_key=True)
    speaker     = Column("speaker", Integer, default=3)
    speed       = Column("speed", Float, default=1)
    pitch       = Column("pitch", Float, default=0)
    intonation  = Column("intonation", Float, default=1)
    volume      = Column("volume", Float, default=1)

Database.Base.metadata.create_all(bind=Database.Engine)
