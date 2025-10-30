from alembic import command
from alembic.config import Config
import os 

alembic_cfg = Config("alembic.ini")
command.upgrade(alembic_cfg, "head")
