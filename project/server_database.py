from sqlalchemy import create_engine, DateTime, MetaData, ForeignKey, Integer, Column, String, Table
from sqlalchemy.orm import mapper, sessionmaker
import datetime


class ServerDataBase:
    class AllUsers:
        def __init__(self, username):
            self.name = username
            self.date_login = datetime.datetime.now()
            self.id = None

    class ActiveUser:
        def __init__(self, user_id, ip_addr, port, date_login):
            self.user = user_id
            self.ip_addr = ip_addr
            self.port = port
            self.date_login = date_login
            self.id = None

    class HistoryLogin:
        def __init__(self, name, date_login, ip, port):
            self.id = None
            self.name = name
            self.date_login = date_login
            self.ip = ip
            self.port = port

    def __init__(self):
        self.database_engine = create_engine('sqlite:///serverdb.db3', echo=False)
        self.metadata = MetaData()

        user_tab = Table('Users', self.metadata,
                         Column('id', Integer, primary_key=True),
                         Column('name', String, unique=True),
                         Column('date_login', DateTime))

        active_user_tab = Table('Active_users', self.metadata,
                                Column('id', Integer, primary_key=True),
                                Column('user', ForeignKey('Users.id'), unique=True),
                                Column('ip_addr', String),
                                Column('port', Integer),
                                Column('date_login', DateTime))

        history_login_tab = Table('History_login', self.metadata,
                                  Column('id', Integer, primary_key=True),
                                  Column('name', ForeignKey('Users.id')),
                                  Column('date_login', DateTime),
                                  Column('ip', String),
                                  Column('port', Integer))

        self.metadata.create_all(self.database_engine)

        mapper(self.AllUsers, user_tab)
        mapper(self.ActiveUser, active_user_tab)
        mapper(self.HistoryLogin, history_login_tab)

        Session = sessionmaker(bind=self.database_engine)
        self.session = Session()

        self.session.query(self.ActiveUser).delete()
        self.session.commit()

    def user_login(self, username, ip_address, port):
        result = self.session.query(self.AllUsers).filter_by(name=username)

        if result.count():
            user = result.first()
            user.date_login = datetime.datetime.now()
        else:
            user = self.AllUsers(username)
            self.session.add(user)
            self.session.commit()

        new_active_user = self.ActiveUser(user.id, ip_address, port, datetime.datetime.now())
        self.session.add(new_active_user)
        history = self.HistoryLogin(user.id, datetime.datetime.now(), ip_address, port)
        self.session.add(history)
        self.session.commit()

    def user_logout(self, username):
        user = self.session.query(self.AllUsers).filter_by(name=username).first()
        self.session.query(self.ActiveUser).filter_by(user=user.id).delete()
        self.session.commit()

    def all_users_list(self):
        lst = self.session.query(self.AllUsers.name, self.AllUsers.date_login)
        return lst.all()

    def all_active_users(self):
        result = self.session.query(
            self.ActiveUser.ip_addr,
            self.ActiveUser.port,
            self.ActiveUser.date_login).join(self.AllUsers)
        return result.all()

    def all_history_login(self, username=None):
        result = self.session.query(self.AllUsers.name,
                                    self.HistoryLogin.date_login,
                                    self.HistoryLogin.ip,
                                    self.HistoryLogin.port).join(self.AllUsers)
        if username:
            result = result.filter(self.AllUsers.name == username)
        return result.all()


if __name__ == '__main__':
    test = ServerDataBase()
    test.user_login('Dima', '192.168.0.2', 9234)
    test.user_login('Liana', '192.168.0.9', 1923)
    print(' ---- all_active_users() ----')
    print(test.all_active_users())
    print('LOGOUT DEF')
    print(test.user_logout('Dima'))
    print(' ---- all_active_users() ----')
    print(test.all_active_users())
    print(' ---- test_db.active_users_list() after logout client_1 ----')
    print(test.all_history_login())
