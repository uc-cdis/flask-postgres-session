from flask.sessions import SessionInterface, SessionMixin
from datetime import timedelta
from uuid import uuid4
from datetime import datetime
from flask_sqlalchemy_session import current_session
from sqlalchemy import Integer, String, Column, Boolean, Text, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base

# 30 minutes
SESSION_TIMEOUT = timedelta(seconds=1800)
# 8 hours
SESSION_LIFETIME = timedelta(seconds=28800)


def user_session_model(table_name="user_session", Base=declarative_base()):
    class UserSession(Base):
        __tablename__ = table_name

        key = Column(String, primary_key=True)
        val = Column(JSONB, default={})
        created_datetime = Column(DateTime, default=datetime.utcnow)
        updated_datetime = Column(
            DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    return UserSession


class PostgresSession(SessionMixin):
    def __init__(self, session):
        self._session = session
        self.modified = False

    @property
    def sid(self):
        return self._session.key

    def get(self, key, *args):
        return self._session.val.get(key, *args)

    def __getitem__(self, key):
        return self._session.val[key]

    def __setitem__(self, key, value):
        self._session.val[key] = value
        self._session.val = dict(self._session.val)
        self.modified = True

    def __delitem__(self, key):
        del self._session.val[key]
        self._session.val = dict(self._session.val)

        self.modified = True

    def __iter__(self):
        for key in self._session.val:
            yield key

    def __len__(self):
        return len(self._session.val)


class PostgresSessionInterface(SessionInterface):

    def __init__(self, session_model):
        super(PostgresSessionInterface, self).__init__()
        self.session_model = session_model

    def open_session(self, app, request):
        sid = request.cookies.get(app.session_cookie_name)
        rv = None
        if not sid:
            sid = str(uuid4())
            rv = self.session_model(key=sid, val={})
        else:
            rv = (
                current_session.query(self.session_model)
                .filter(self.session_model.key == sid).first())
            if not rv:
                rv = self.session_model(key=sid, val={})

        return PostgresSession(rv)

    def get_expiration_time(self, app, session):
        # the session expire if the user is inactive for
        # SESSION_TIMEOUT seconds or the user has been active
        # in for SESSION_LIFETIME seconds
        return min(
            session._session.updated_datetime
            + (app.config.get('SESSION_TIMEOUT') or SESSION_TIMEOUT),
            session._session.created_datetime
            + (app.config.get('SESSION_LIFETIME') or SESSION_LIFETIME))

    def save_session(self, app, session, response):
        domain = self.get_cookie_domain(app)
        if session.modified:
            session._session = current_session.merge(session._session)
            current_session.commit()

        if session._session.updated_datetime:
            # if the session has updated datetime then it's a session from db
            cookie_exp = self.get_expiration_time(app, session)
            if cookie_exp < datetime.utcnow():  # delete expired session
                current_session.delete(session._session)

            response.set_cookie(
                app.session_cookie_name, session.sid,
                expires=cookie_exp, httponly=True, domain=domain)
