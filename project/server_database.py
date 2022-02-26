from sqlalchemy import create_engine, DateTime, MetaData, ForeignKey, Integer, Column, String, Table
from sqlalchemy.orm import mapper, sessionmaker
import datetime


class ServerDataBase:
    class AllUsers:
        def __init__(self, username):
            self.name = username
            self.last_login = datetime.datetime.now()
            self.id = None

    class ActiveUsers:
        def __init__(self, user_id, ip_address, port, login_time):
            self.user = user_id
            self.ip_address = ip_address
            self.port = port
            self.login_time = login_time
            self.id = None

    class HistoryLogin:
        def __init__(self, name, date_time, ip, port):
            self.id = None
            self.name = name
            self.date_time = date_time
            self.ip = ip
            self.port = port

    class UserContacts:
        def __init__(self, user, contact):
            self.id = None
            self.user = user
            self.contact = contact

    class UserHistory:
        def __init__(self, user):
            self.id = None
            self.user = user
            self.send = 0
            self.accepted = 0

    def __init__(self, path):
        self.database_engine = create_engine(f'sqlite:///{path}', echo=False, pool_recycle=7200,
                                             connect_args={'check_same_thread': False})

        self.metadata = MetaData()
        users_table = Table('Users', self.metadata,
                            Column('id', Integer, primary_key=True),
                            Column('name', String, unique=True),
                            Column('last_login', DateTime)
                            )

        active_users_table = Table('Active_users', self.metadata,
                                   Column('id', Integer, primary_key=True),
                                   Column('user', ForeignKey('Users.id'), unique=True),
                                   Column('ip_address', String),
                                   Column('port', Integer),
                                   Column('login_time', DateTime))

        user_login_history = Table('Login_history', self.metadata,
                                   Column('id', Integer, primary_key=True),
                                   Column('name', ForeignKey('Users.id')),
                                   Column('date_time', DateTime),
                                   Column('ip', String),
                                   Column('port', String)
                                   )

        contacts = Table('Contacts', self.metadata,
                         Column('id', Integer, primary_key=True),
                         Column('user', ForeignKey('Users.id')),
                         Column('contact', ForeignKey('Users.id'))
                         )

        users_history_table = Table('History', self.metadata,
                                    Column('id', Integer, primary_key=True),
                                    Column('user', ForeignKey('Users.id')),
                                    Column('send', Integer),
                                    Column('accepted', Integer)
                                    )

        self.metadata.create_all(self.database_engine)

        mapper(self.AllUsers, users_table)
        mapper(self.ActiveUsers, active_users_table)
        mapper(self.HistoryLogin, user_login_history)
        mapper(self.UserContacts, contacts)
        mapper(self.UserHistory, users_history_table)

        Session = sessionmaker(bind=self.database_engine)
        self.session = Session()

        self.session.query(self.ActiveUsers).delete()
        self.session.commit()

    def user_login(self, username, ip_address, port):
        result = self.session.query(self.AllUsers).filter_by(name=username)

        if result.count():
            user = result.first()
            user.login_time = datetime.datetime.now()
        else:
            user = self.AllUsers(username)
            self.session.add(user)
            self.session.commit()
            user_in_history = self.UserHistory(user.id)
            self.session.add(user_in_history)

        new_active_user = self.ActiveUsers(user.id, ip_address, port, datetime.datetime.now())
        self.session.add(new_active_user)
        history = self.HistoryLogin(user.id, datetime.datetime.now(), ip_address, port)
        self.session.add(history)
        self.session.commit()

    def user_logout(self, username):
        user = self.session.query(self.AllUsers).filter_by(name=username).first()
        self.session.query(self.ActiveUsers).filter_by(user=user.id).delete()
        self.session.commit()

    def users_list(self):
        query = self.session.query(
            self.AllUsers.name,
            self.AllUsers.last_login
        )
        return query.all()

    def all_active_users(self):
        result = self.session.query(
            self.AllUsers.name,
            self.ActiveUsers.ip_address,
            self.ActiveUsers.port,
            self.ActiveUsers.login_time).join(self.AllUsers)
        return result.all()

    def all_history_login(self, username=None):
        result = self.session.query(self.AllUsers.name,
                                    self.HistoryLogin.date_time,
                                    self.HistoryLogin.ip,
                                    self.HistoryLogin.port).join(self.AllUsers)
        if username:
            result = result.filter(self.AllUsers.name == username)
        return result.all()

    def add_contact(self, user, contact):
        # Получаем ID пользователей
        user = self.session.query(self.AllUsers).filter_by(name=user).first()
        contact = self.session.query(self.AllUsers).filter_by(name=contact).first()

        # Проверяем что не дубль и что контакт может существовать (полю пользователь мы доверяем)
        if not contact or self.session.query(self.UserContacts).filter_by(user=user.id, contact=contact.id).count():
            return

        # Создаём объект и заносим его в базу
        contact_row = self.UserContacts(user.id, contact.id)
        self.session.add(contact_row)
        self.session.commit()

    def remove_contact(self, user, contact):
        user = self.session.query(self.AllUsers).filter_by(name=user).first()
        contact = self.session.query(self.AllUsers).filter_by(name=contact).first()
        if not contact:
            return

        print(self.session.query(self.UserContacts).filter(
            self.UserContacts.user == user.id,
            self.UserContacts.contact == contact.id
        ).delete())
        self.session.commit()

    def get_contacts(self, username):
        user = self.session.query(self.AllUsers).filter_by(name=username).one()
        answer = self.session.query(self.UserContacts, self.AllUsers.name).filter_by(user=user.id).join(self.AllUsers,
                                                                                                        self.UserContacts.contact == self.AllUsers.id)
        return [contact[1] for contact in answer.all()]

    def process_message(self, sender, recipient):
        sender = self.session.query(self.AllUsers).filter_by(name=sender).first().id
        recipient = self.session.query(self.AllUsers).filter_by(name=recipient).first().id
        sender_row = self.session.query(self.UserHistory).filter_by(user=sender).first()
        sender_row.sent += 1
        recipient_row = self.session.query(self.UserHistory).filter_by(user=recipient).first()
        recipient_row.accepted += 1

        self.session.commit()

    def message_history(self):
        query = self.session.query(
            self.AllUsers.name,
            self.AllUsers.last_login,
            self.UserHistory.send,
            self.UserHistory.accepted
        ).join(self.AllUsers)

        return query.all()


if __name__ == '__main__':
    if __name__ == '__main__':
        test_db = ServerDataBase('server_base.db3')
        test_db.user_login('1111', '192.168.1.113', 8080)
        test_db.user_login('McG2', '192.168.1.113', 8081)
        print(test_db.all_users_list())
        print(test_db.all_active_users())
        test_db.user_logout('McG2')
        print(test_db.all_history_login('re'))
        test_db.add_contact('test2', 'test1')
        test_db.add_contact('test1', 'test3')
        test_db.add_contact('test1', 'test6')
        test_db.remove_contact('test1', 'test3')
        test_db.process_message('McG2', '1111')
        print(test_db.message_history())
