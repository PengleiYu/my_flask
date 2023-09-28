import os

from app import create_app, db
from app.models import User, Role
from flask_migrate import Migrate

app = create_app(os.getenv("FLASK_CONFIG") or 'default')
migrate = Migrate(app, db)


@app.shell_context_processor
def make_shell_context():
    # todo 目前第一次部署时必须手动执行db创建过程
    return dict(db=db, User=User, Role=Role)


@app.cli.command()
def test():
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
