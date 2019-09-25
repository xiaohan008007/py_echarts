
from flask_script import Manager, Server
from server import create_app
import subprocess
import sys

manager = Manager(create_app)
manager.add_command("runserver",
                    Server(host="0.0.0.0", use_debugger=True, port=9963, threaded=True, use_reloader=True))


@manager.command
def lint():
    """Runs code linter."""
    lint = subprocess.call(['flake8', '--ignore=E402', 'title_scoring/', 'manage.py', 'tests/']) == 0
    if lint:
        print('OK')
    sys.exit(lint)


if __name__ == '__main__':
    manager.run()
