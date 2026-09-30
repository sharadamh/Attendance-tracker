"""
Application factory.
Creates and configures the Flask application instance.
"""
from flask import Flask
from .config import config_map
from .extensions import db, migrate


def create_app(config_name: str = "default") -> Flask:
    """
    Create a configured Flask application.

    Args:
        config_name: Key into config_map ('default', 'testing', 'development').

    Returns:
        Configured Flask app instance.
    """
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="../static",   # static/ lives at project root level
    )

    # Load configuration from the config map
    app.config.from_object(config_map[config_name])

    # Initialise extensions with the app
    db.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints (API routes)
    from .routes.students import students_bp
    from .routes.employees import employees_bp
    from .routes.attendance import attendance_bp
    from .routes.reports import reports_bp
    from .routes.views import views_bp

    app.register_blueprint(views_bp)
    app.register_blueprint(students_bp, url_prefix="/api/students")
    app.register_blueprint(employees_bp, url_prefix="/api/employees")
    app.register_blueprint(attendance_bp, url_prefix="/api/attendance")
    app.register_blueprint(reports_bp, url_prefix="/api/reports")

    # Ensure all tables are created on first run
    with app.app_context():
        db.create_all()

    return app
