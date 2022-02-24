from sqlalchemy import Table, String, Integer, DateTime, MetaData, Column, Text, create_engine
from sqlalchemy.orm import sessionmaker, mapper
import datetime


class ClientDataBase:
    class ExistUser:
        def __init__(self, user):
            self.id = None
            self.user = user

    class MessageHistory:
        def __init__(self, from_user, to_user, message):
            self.id = None
            self.from_user = from_user
            self.to_user = to_user
            self.message = message
            self.date = datetime.datetime.now()

    class Contacts:
        def __init__(self, name):
            self.username = name

    def __init__(self, name):
        self.engine = create_engine(f'sqlite:///clientdb_{name}.db3', echo=False,
                                    connect_args={'check_same_thread': False})
        self.metadata = MetaData()

        exist_users = Table('exist_users', self.metadata,
                            Column('id', Integer, primary_key=True),
                            Column('user', String))

        messaqe_history = Table('message_history', self.metadata,
                                Column('id', Integer, primary_key=True),
                                Column('from_user', String),
                                Column('to_user', String),
                                Column('message', Text),
                                Column('date', DateTime))

        contacts = Table('contacts', self.metadata,
                         Column('id', Integer, primary_key=True),
                         Column('username', String, unique=True))

        self.metadata.create_all(self.engine)

        mapper(self.ExistUser, exist_users)
        mapper(self.MessageHistory, messaqe_history)
        mapper(self.Contacts, contacts)

        Session = sessionmaker(self.engine)
        self.session = Session()

        self.session.query(self.Contacts).delete()
        self.session.query(self.ExistUser).delete()
        self.session.commit()

    def add_users(self, users_list):
        for user in users_list:
            user_know = self.ExistUser(user=user)
            self.session.add(user_know)
        self.session.commit()

    def add_contact(self, user):
        if not self.session.query(self.Contacts).filter_by(username=user).count():
            contact = self.Contacts(user)
            self.session.add(contact)
            self.session.commit()

    def contact_del(self, user):
        self.session.query(self.Contacts).filter_by(username=user).delete()
        self.session.commit()

    def save_message(self, from_user, to_user, message):
        message_save = self.MessageHistory(from_user, to_user, message)
        self.session.add(message_save)
        self.session.commit()

    def get_contact(self):
        return [contact[0] for contact in self.session.query(self.Contacts.username).all()]

    def get_users(self):
        return [contact[0] for contact in self.session.query(self.ExistUser.user).all()]

    def check_user(self, user):
        if self.session.query(self.ExistUser).filter_by(user=user).count():
            return True
        return False

    def check_contact(self, name):
        if self.session.query(self.Contacts).filter_by(username=name):
            return True
        else:
            return False

    def get_history(self, from_user=None, to_user=None):
        if from_user:
            query = self.session.query(self.MessageHistory).filter_by(from_user=from_user)
        if to_user:
            query = self.session.query(self.MessageHistory).filter_by(to_user=to_user)

        return [(history.from_user, history.to_user, history.message, history.date)
                for history in query.all()]


if __name__ == '__main__':
    testdb = ClientDataBase('Dima')
    testdb.add_users(['Dima', 'Liana', 'Masha'])
    testdb.add_users(['Kirill'])
    for i in (['Dima', 'Liana', 'Masha']):
        testdb.contact_add(i)
    # print(testdb.check_contact('Oleg'))
    print(testdb.check_user('Kirill'))
    print(testdb.check_user('Anna'))
    # print(testdb.save_message('Dima', 'Liana', f'Привет! я тестовое сообщение от {datetime.datetime.now()}!'))
    # print(testdb.save_message('Liana', 'Dima', f'Привет! я другое тестовое сообщение от {datetime.datetime.now()}!'))
    print(testdb.get_history('Liana'))
    print(testdb.get_history(from_user='Dima'))
    print(testdb.get_contact())
    print(testdb.get_users())
    print(testdb.check_user('Kirill'))
    print(testdb.check_user('Anna'))
    testdb.contact_del('Masha')
    print(testdb.get_contact())
