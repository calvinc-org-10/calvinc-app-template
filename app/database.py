
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# rootdir = "."
# app_dbName = f"{rootdir}\\appdb.sqlite"
app_dbName = f"appdb.sqlite"

# an Engine, which the Session will use for connection
# resources, typically in module scope
app_engine = create_engine(
    f"sqlite:///{app_dbName}",
    )
# a sessionmaker(), also in the same scope as the engine
_app_Session = sessionmaker(app_engine)

def get_app_session():
    return _app_Session()
def get_app_sessionmaker():
    return _app_Session

##########################################################
###################    REPOSITORIES    ###################
##########################################################

from cMenu.database import Repository
