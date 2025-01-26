import os
import unittest

from flask.cli import FlaskGroup
from app.main import create_app
from app import blueprint

flask_env = os.environ.get('FLASK_ENV')
print(flask_env)
app = create_app(flask_env)
app.register_blueprint(blueprint)
app.app_context().push()

cli = FlaskGroup(app)


@cli.command
def run():
    cli()

if __name__ == '__main__':
    cli()