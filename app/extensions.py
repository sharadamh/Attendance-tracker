"""
Flask extension instances are created here (without an app object).
They are initialised later in the application factory via init_app().
This pattern avoids circular imports.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# SQLAlchemy ORM instance — imported by models
db = SQLAlchemy()

# Flask-Migrate instance — handles Alembic migrations
migrate = Migrate()
