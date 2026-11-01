from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import pickModelBase

rootdir = "."
app_dbName = f"{rootdir}/appdb.sqlite"

# Create SQLite database engine
# which the Session will use for connection
# resources, typically in module scope
app_engine = create_engine(
    f"sqlite:///{app_dbName}",
    )
# a sessionmaker(), also in the same scope as the engine
_app_Session = sessionmaker(app_engine)

# Create all tables in the database
pickModelBase.metadata.create_all(app_engine)

# Create a customized Session class
_app_session = sessionmaker(bind=app_engine)

def get_app_session():
    return _app_session()
def get_app_sessionmaker():
    return _app_session

from calvincTools.database import Repository
