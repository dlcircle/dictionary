DIALECT = 'mysql'
DRIVER = 'mysqldb'
USERNAME = 'root'
PASSWORD = 'qiuji1991'
# PASSWORD = 'DmR2B@xBr2'
HOST = 'localhost'
PORT = '3306'
DATABASE = 'dictionary'

# SQLALCHEMY_DATABASE_URI = "{}+{}://{}:{}@{}:{}/{}?charset=utf8".format(DIALECT, DRIVER, USERNAME, PASSWORD, HOST, PORT, DATABASE)
SQLALCHEMY_DATABASE_URI = 'mysql+mysqldb://root:qiuji1991@localhost:3306/dictionary?charset=utf8'
SQLALCHEMY_ENCODING = 'utf-8'
SQLALCHEMY_TRACK_MODIFICATIONS = False  # 屏蔽 sql alchemy 的 FSADeprecationWarning