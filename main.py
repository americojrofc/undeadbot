#!/usr/bin/python3

from os import environ
import logging 
import argparse
from functools import lru_cache
from time import time
from requests.exceptions import ReadTimeout

import telebot
from database import user_exist, user_amount_alerts, new_alert, reset_alerts
# TODO: configura level debug atráves do argparse
#
logger = logging.getLogger('main')

# busca o token na variavel de ambiente
TOKEN = environ['BOT_KEY']
# máxio de alertas antes de banir
MAX_ALERTS = 5
# tempo de banir
BAN_SECS = 86400 * 7 # 1 dia = 86400 segundos
# afirma que token deve existir
assert TOKEN != None, "Defina a variavel de ambiente: export BOT_KEY='{}'"
# obtem uma instancia usando o token
bot = telebot.TeleBot(TOKEN, skip_pending=True)

@bot.message_handler(commands=['help'])
def send_help(msg):
    logger.debug('Received message from user: %d' %msg.from_user.id)
    bot.send_message(msg.chat.id, 'Helper message Working...')
    
@bot.message_handler(content_types=['new_chat_members'])
def handle_new_member(msg):
    banner = "Seja bem vindo, {}!\
    Regras: undeadsec.github.io"
    bot.send_message(msg.chat.id, banner.format(msg.new_chat_member.first_name))

@bot.message_handler(func=lambda msg: msg.chat.type in 'supergroup' and not is_admin(msg.from_user.id, msg.chat.id), content_types=['sticker'])
def scan_messages(msg):
    logger.debug("'Scaniando' mensagem")
    
    new_alert(msg.from_user.id) # adiciona 1 alerta pela infração
    user_alerts = user_amount_alerts(msg.from_user.id)
        
    if user_alerts >= MAX_ALERTS:
        bot.reply_to(msg, 'Banido por excesso de stickers!')
        until_date = time() + BAN_SECS
        bot.kick_chat_member(msg.chat.id, msg.from_user.id, until_date=until_date)
        reset_alerts(msg.from_user.id)
    
    elif user_alerts == MAX_ALERTS - 1:
        bot.reply_to(msg, '%s você será banido por uma semana na próxima vez que enviar um sticker!'%msg.from_user.first_name)
    else:
        bot.reply_to(msg, '%s é proibido enviar stickers nesse grupo. Notificação %d/%d' %(msg.from_user.first_name, user_alerts, MAX_ALERTS))


def is_admin(uid, cid):
    admins = get_admins_from_chat(cid)
    return uid in admins

def get_admins_from_chat(cid):
    _admins = bot.get_chat_administrators(cid)
    return [admin.user.id for admin in _admins]

def configure_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', help='Nivel do debug, (INT|STRING)')
    parser.add_argument('-o', '--output', type=str, help='Arquivo para saida')
    
    args = parser.parse_args()
    # configura level do debug
    level = 'NOTSET' if not args.debug else args.debug
    logger.setLevel(level)
    
    # especifica formato de saida
    FORMAT = "%(asctime)-15s %(name)-8s %(message)s'"
    filename = None if not args.output else args.output
    logging.basicConfig(format=FORMAT, filename=filename, filemode='w')
    logger.debug('Parser configurado!')
    
if __name__ == '__main__':
    configure_parser()
    # TODO: não está salvando log no arquivo
    print('running...')
    bot.polling(none_stop=True, interval=5, timeout=600)
