# -*- coding: utf-8 -*-
"""
Create by wang_yang1980@hotmail.com at 7/3/19
"""
import os

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, scoped_session
import sqlparse
from robot.utils import ConnectionCache
from robot.api import logger

from .base import HybridCore
from .base import keyword
from .version import VERSION

os.environ["NLS_LANG"] = ".UTF8"


class DatabaseLib(HybridCore):
    """
    DatabaseLib is created based on [https://www.sqlalchemy.org/|sqlalchemy].

    It support below features:
    - Database operations(select/insert/update/delete...)
    - Multi database connections, user could use "Switch Connection" to change current connection
    - ORM extension support
    - Extension this libraries easily
    """
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    ROBOT_LIBRARY_VERSION = VERSION

    def __init__(self, libraryComponents=[]):
        """
        DatabaseLib could be extened through parameter libraryComponents
        """
        self._connections = ConnectionCache()
        self._sessions = {}
        super(DatabaseLib, self).__init__(libraryComponents)

    @property
    def current(self):
        return self._connections.current

    @property
    def session(self):
        if self.current not in self._sessions:
            raise RuntimeError('Session is not created!')
        return self._sessions[self.current]

    @keyword
    def connect_to_db(self, hostOrUrl, port=None, database=None, user=None, password=None, dbPrefix=None, alias=None,
                      **kwargs):
        """
        Connect to database  [http://docs.sqlalchemy.org/en/latest/core/engines.html|sqlalchemy]

        :param hostOrUrl: database hostname or database connection string
        :param port: database port
        :param database: database name
        :param user: database user name
        :param password: database password
        :param dbPrefix: format is dialect+driver, dialect is optional
        :param alias: connection alias, could be used to switch connection
        :param kwargs: please check [http://docs.sqlalchemy.org/en/latest/core/engines.html|create_engine] to get more details
        :return:  connection index

        Example:
        | Connect To Db | 127.0.0.1 | 3306 | test | user | password | mysql |
        | Connect To Db | mysql://user:password@127.0.0.1:3306/test?charset=utf8 |

        """
        if '://' in hostOrUrl:
            connectStr = hostOrUrl
        elif 'mysql' in dbPrefix.lower():
            connectStr = '%s://%s:%s@%s:%s/%s?charset=utf8' % (dbPrefix, user, password, hostOrUrl, port, database)
        else:
            connectStr = '%s://%s:%s@%s:%s/%s' % (dbPrefix, user, password, hostOrUrl, port, database)
        logger.debug('Connection String: {0}'.format(connectStr))
        engine = create_engine(connectStr, **kwargs)
        connectionIndex = self._connections.register(engine, alias)
        return connectionIndex

    @keyword
    def switch_connection(self, indexOrAlias):
        """
        Switch database connection

        :param indexOrAlias: connection alias or index
        :return:  previous index

        Example:
        | Connect To Db | 127.0.0.1 | 3306 | test1 | user | password | mysql | connection_1 |
        | Connect To Db | 127.0.0.1 | 3306 | test2 | user | password | oracle | connection_2 |
        | Switch Connection | connection_1 |
        """
        oldIndex = self._connections.current_index
        self._connections.switch(indexOrAlias)
        return oldIndex

    @keyword
    def create_session(self, autoflush=True, autocommit=False, expireOnCommit=True, info=None, **kwargs):
        """
        Create session based on current connection(engine)

        if session is already for current connection, keyword will return created session directly.
        This keyword could be used to extend library with ORM

        :param autoflush: default value is True
        :param autocommit: default value is False
        :param expireOnCommit: default value is True
        :param info: default value is None
        :param kwargs: Please check Session in sqlalchemy
        :return: session
        """
        if self.current in self._sessions:
            return self._sessions[self.current]
        elif self.current is not None:
            self.current.echo = 'debug'
            session = scoped_session(sessionmaker(bind=self.current, autoflush=autoflush, autocommit=autocommit,
                                                  expire_on_commit=expireOnCommit, info=info, **kwargs))
            self._sessions[self.current] = session
            return session
        raise RuntimeError('Current connection may closed, or not create connection yet!')

    @keyword
    def close_connection(self):
        """
        Close current database connection

        :return: None
        """
        if self.current in self._sessions:
            self._sessions.pop(self.current)
        self.current.dispose()
        self._connections.current = self._connections._no_current

    @keyword
    def close_all_connections(self):
        """
        Close all database connections

        :return: None
        """
        self._sessions.clear()
        self._connections.close_all('dispose')

    @keyword
    def execute(self, sql):
        """
        Execute sql

        :param sql:  sql
        :return: sqlalchemy ResultProxy
        """
        return self.current.execute(sql)

    @keyword
    def query(self, sql, *args, **kwargs):
        """
        Execute query

        :param sql: sql string
        :param args: if params in sql want to be replaced by index, use args
        :param kwargs: if params in sql want to be replaced by key, use kwargs
        :return: List of ResultProxy

        Examples:

        | ${results}= | Query |   SELECT {0}, {1} FROM MY_TABLE         |   c1   |  c2    |
        | ${results}= | Query |   SELECT {col1}, {col2} FROM MY_TABLE   | col1=c1 | col2=c2 |
        | ${results}= | Query |   SELECT c1, c2 FROM MY_TABLE           |        |        |
        """
        if not args:
            args = []
        if not kwargs:
            kwargs = {}
        sql = sql.format(*args, **kwargs)
        logger.debug('Execute: %s' % sql)
        resultProxy = self.execute(sql)
        results = [result for result in resultProxy]
        logger.debug('Results: %s' % results)
        return results

    @keyword
    def execute_sql_script(self, sqlFile):
        """
        Execute sql script file

        :param sqlFile: Path to sql script file, not format should be utf-8
        :return: None
        """
        with open(sqlFile, 'r', encoding='utf-8') as f:
            content = f.read()
        content = content.replace('\ufeff', '')
        sqlStrList = sqlparse.split(sqlparse.format(content, strip_comments=True))
        sqlStrList = [sqlparse.format(sqlStr.strip(';'), keyword_case='upper', reindent=True)
                      for sqlStr in sqlStrList if sqlStr.strip()]
        for sqlStr in sqlStrList:
            self.execute(sqlStr)

    @keyword
    def call_stored_procedure(self, name, *params):
        """
        Call stored procedure

        :param name: name of stored procedure
        :param params: parameters of stored procedure
        :return: results
        """
        connection = self.current.raw_connection()
        try:
            cursor = connection.cursor()
            results = cursor.callproc(name, params)
            cursor.close()
            connection.commit()
        finally:
            connection.close()
        return results
