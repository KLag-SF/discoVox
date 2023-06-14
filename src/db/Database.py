import sqlalchemy
from sqlalchemy.orm import declarative_base, scoped_session ,sessionmaker

from src import discordSettings

user = discordSettings.MY_USER
passwd = discordSettings.MY_PASS
addr = discordSettings.MY_ADDR
name = discordSettings.MY_DB

conn = f"mysql+mysqlconnector://{user}:{passwd}@{addr}/{name}"

Engine = sqlalchemy.create_engine(conn, echo=False)
Session = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=Engine)
)
Base = declarative_base()