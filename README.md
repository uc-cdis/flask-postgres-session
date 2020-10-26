# flask-postgres-session
server side user session for flask app with postgres as backend

## Usage
To use this session library, first instantiate sqlalchemy table class with a table name, if not given, the table name will be "user_session", then specify your flask app to use this session interface:
```
models.py:

    from flask_postgres_session import user_session_model
    from sqlalchemy.ext.declarative import declarative_base

    Base = declarative_base()
    UserSession = user_session_model('servicename_user_session', Base=Base)


__init__.py:

    from flask_postgres_session import PostgresSessionInterface
    from .models import *

    app.session_interface = PostgresSessionInterface(UserSession)

```

Then in your view you can access the session as a dict:

```
from flask import session

@app.route("/")
def test():
    if not session.get('testdata'):
        session['testdata'] = 'abc'
```
The default session's timeout (max inactive session lifetime) is 30 min and lifetime (max session lifetime) is 8 h, if you want to change that, you should define SESSION_TIMEOUT/SESSION_LIFETIME in your flask app.config.
