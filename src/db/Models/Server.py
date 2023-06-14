from sqlalchemy import Column, String
from src.db import Database

class Server(Database.Base):
    """
    Model: Server
    Store server and target channel
    """
    __tablename__ = "Servers"
    server_ID   = Column(String(32), primary_key=True)
    channel     = Column(String(32))

Database.Base.metadata.create_all(bind=Database.Engine)