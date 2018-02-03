import logging
from pony.orm import Database, Required, db_session, select, PrimaryKey

logger = logging.getLogger('main.database')

db = Database()

class User(db.Entity):
    uid = PrimaryKey(int)
    alerts = Required(int)

db.bind(provider='sqlite', filename='database.sqlite', create_db=True)
db.generate_mapping(create_tables=True)

@db_session
def user_exist(uid):
    logger.debug('Checando existência de usuário ID: %d' %uid)
    return True if User.get(uid=uid) else None

@db_session
def create_user(uid, alerts=0):
    logger.debug('Criando usuário ID: %d' %uid)
    User(uid=uid, alerts=alerts)

@db_session
def new_alert(uid):
    logger.debug('Adicionar alerta para usuário ID: %d' %uid)
    if not user_exist(uid):
        create_user(uid)
        
    user = User[uid]
    user.alerts += 1

@db_session
def user_amount_alerts(uid):
    logger.debug('Consultando quantidade de alertas usuário ID: %d' %uid)
    if not user_exist(uid):
        create_user(uid)
    user = User[uid]
    return user.alerts

@db_session
def reset_alerts(uid):
    logger.debug('Limpando alertas do usuário ID: %d' %uid)
    user = User[uid]
    user.alerts = 0
        
