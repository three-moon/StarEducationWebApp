from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = "user.select_login"
login.login_message = u"Для доступа к платформе выполните вход в систему"
login.login_message_category = "dark"
bootstrap = Bootstrap()

