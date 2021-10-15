from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from conf.settings import DATABASES


class DbFactory:
    """
        数据库工厂
    """

    def __init__(self, db_mapping: str = 'default', engine_str: str = None, host: str = None, db_name: str = None,
                 user: str = None,
                 pwd: str = None):
        db_options = DATABASES.get(db_mapping)
        self.engine_str = engine_str if engine_str else db_options.get('ENGINE')
        self.host = host if host else db_options.get('HOST')
        self.port = db_options.get('POST')
        self.db_name = db_name if db_name else db_options.get('NAME')
        self.user = user if user else db_options.get('USER')
        self.password = pwd if pwd else db_options.get('PASSWORD')
        # self.engine = create_engine("mysql+pymysql://root:admin123@localhost/searchrescue", encoding='utf-8', echo=True)
        # TODO:[-] 21-09-29 新加入的 每次使用 session 之前进行简单的查询检查，判断 session是否过期
        # 参考文章: https://www.cnblogs.com/lesliexong/p/8654615.html
        # self.engine = create_engine(
        #     f"mysql+{self.engine_str}://{self.user}:{self.password}@{self.host}:{self.port}/{self.db_name}",
        #     encoding='utf-8', echo=True, pool_pre_ping=True)
        self.engine = create_engine(
            f"mysql+{self.engine_str}://{self.user}:{self.password}@{self.host}:{self.port}/{self.db_name}",
            encoding='utf-8',pool_pre_ping=True)
        self._session_def = sessionmaker(bind=self.engine)

    @property
    def Session(self) -> sessionmaker:
        if self._session_def is None:
            self._session_def = sessionmaker(bind=self.engine)
        return self._session_def()
