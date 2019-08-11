import os
import logging

log = logging.getLogger(__name__)

import telebot
from telebot import util

# busca o token na variavel de ambiente
TOKEN = os.environ['BOT_KEY']
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['help', 'Help'])
def send_welcome(message):
    if message.chat.type == 'supergroup' or message.chat.type == 'group':
        bot.reply_to(message, '''**UNDEADBOT**

BASIC
/help : to access help menu
/rules : to see rules of the group       

TOOLS
/ping : to do ping on hosts
/testip 8.8.8.8: to see if an IP is on
/whois : to do whois check        
        ''')
def is_private(message):
        """verifica se o chat é privado
        param: obj telebot message
        return: bool"""
        log.info('Checking type chat...')
        return message.chat.type == 'private'

@bot.message_handler(commands=['rules', 'Rules'])
def send_rules(message):
    # verifica se o chat é um group ou supergrop
    if message.chat.type in 'supergroup':
        bot.reply_to(message, "Look at our rules in undeadsec.github.com")


@bot.message_handler(func=is_private, commands=['ping', 'Ping'])
def verify_ip_online(message):
    # extrai o argumento que deve ser o ip
    ip = util.extract_arguments(message.text)
    log.debug('Verifing if ip %r is online', ip)
    # executa o ping e verfica o código de retorno
    result = os.system("ping -c1 -W 1 %s > /dev/null" %ip)
    # TODO: usar regex para filtrar o ip evitando command inject
    if result == 0:
        bot.reply_to(message, "%s is working !" %ip)
    else:
        bot.reply_to(message, "%s is not working !" %ip)  


@bot.message_handler(func=is_private, commands=['whois'])
def execute_whois(message):
    if message.chat.type in 'supergroup': # Filtra group e supergroup
        message_received = message.text.split()
        r = os.system("whois {} > results/whois.txt".format(message_received[1]))
        result = open('results/whois.txt', 'r')
        bot.reply_to(message, ping_result)                 


@bot.message_handler(content_types=['new_chat_members'])
def send_welcome_new_members(message):
    bot.reply_to(message, "Hey, welcome to UndeadSec !\nType /rules to see the rules.")   


if __name__ == '__main__':
    # ignora logs do urllib3
    logging.getLogger('urllib3').setLevel(logging.CRITICAL)

    # configura logging para debug
    logging.basicConfig(level=logging.DEBUG)
    
    print('running...')
    bot.polling()
