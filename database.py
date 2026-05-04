from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import pickModelBase

rootdir = "."
app_dbName = f"{rootdir}/appdb.sqlite"

# Create SQLite database engine
engine = create_engine(
    f'sqlite:///{app_dbName}', 
    echo=False
    )

# Create all tables in the database
pickModelBase.metadata.create_all(engine)

# Create a customized Session class
Session = sessionmaker(bind=engine)

def get_app_session():
    return Session()
def get_app_sessionmaker():
    return Session

from calvincTools.database import Repository
