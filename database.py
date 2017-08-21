from pony.orm import *


db = Database()


class Eventos(db.Entity):
    id = PrimaryKey(int, auto=True)
    criado_timestamp = Optional(float, nullable=True)
    criado_por = Optional(float, nullable=True)
    grupo = Optional(float, nullable=True)
    titulo = Optional(str, nullable=True)
    acontece_timestamp = Optional(float, nullable=True)

def criar_evento(criado_timestamp, criado_por, grupo, titulo, acontece_timestamp):
    with db_session:
        Eventos(
            criado_timestamp=criado_timestamp,
            criado_por=criado_por,
            grupo=grupo,
            titulo=titulo,
            acontece_timestamp=acontece_timestamp
            )

def buscar_eventos_grupo(grupo):
    with db_session:
        return select((e.titulo, e.acontece_timestamp) for e in Eventos if e.grupo == grupo)[:]