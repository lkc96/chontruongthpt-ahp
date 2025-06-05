from flask import Flask
from flask_sqlalchemy import SQLAlchemy # type: ignore



db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)

    from app.routes import schools
    app.register_blueprint(schools.bp)
    from app.routes import map
    app.register_blueprint(map.bp)
    app.jinja_env.globals.update(enumerate=enumerate)

    return app