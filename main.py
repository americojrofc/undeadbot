from datetime import datetime
import logging
from os import getenv

import telebot
from telebot import util
from database import db, criar_evento, buscar_eventos_grupo

logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)

#create and bind database 
db.bind(provider='sqlite', filename='database.sqlite', create_db=True)
db.generate_mapping(create_tables=True)

#binding token
api_key = getenv('BOT_TOKEN')
if not api_key: exit('Api key not found on env!')

bot = telebot.TeleBot(api_key)


@bot.message_handler(content_types=['new_chat_members'])
def handle_new_member(msg):
	banner = "{} Seja bem vindo a Matrix, eu sou Smith e \
	estou aqui para assegurar a ordem e o funcionamento do sistema."
	bot.send_message(msg.chat.id, banner.format(msg.new_chat_member.first_name))


@bot.message_handler(regexp=r"^(\/novo [\w ]{1,43}) ([0-9]+\/[0-9]+\/[0-9]+) ([0-9]+\:[0-9]+)$")
def handle_new_events(msg):
   
    arguments = util.extract_arguments(msg.text).split() # type: list
    title = arguments[:-2] 
    title = ' '.join(title) # type: str
    fmtdate = ' '.join(arguments[-2:])
    fmtdate = format_datetime(fmtdate) # type: datetime

    if fmtdate:
        criado_timestamp = datetime.now().timestamp()
        criado_por = msg.from_user.id # type: float
        grupo = msg.chat.id # type: float
        titulo = title
        acontece_timestamp = fmtdate.timestamp()
        criar_evento(criado_timestamp, criado_por, grupo, titulo, acontece_timestamp)
        
        bot.send_message(msg.chat.id, "{}  {} criado!".format(titulo, fmtdate.strftime("%d/%m/%Y %H:%M")))
    else:
        bot.send_message(msg.chat.id, "Tente no formato 'titulo DD/MM/YYYY HH:MM'")
        
def format_datetime(arg):
    if not arg: return
    try:
        dr = datetime.strptime(arg,  "%d/%m/%Y %H:%M")
        return dr
    except ValueError:
        return

@bot.message_handler(commands=['eventos', 'Eventos'])
def show_events(msg):
    events = buscar_eventos_grupo(msg.chat.id) # type: tuple
    all_events = ''
    for title, timestamp in events:
        day = datetime.fromtimestamp(timestamp).strftime("%d/%m/%Y %H:%M")
        all_events += "{} {}\n".format(title, day)
    bot.send_message(msg.chat.id, all_events)


@bot.message_handler(commands=['meuseventos'])
def show_user_events(msg):
    pass


if __name__ == "__main__":
    print('Executando...')
    bot.polling(none_stop=False, timeout=120)
