from discord import *
from replit import db
from keep_alive import keep_alive
import pytz
import re
from datetime import datetime
import os

client = Client()
token = os.getenv('TOKEN')

def is_all_or_equal(arg_1, arg_2):
  if arg_1 == 'All' or arg_2 == 'All':
    return True
  else:
    return arg_1 == arg_2

def date_list_controller(date_list, date_int):
  if date_list == ['All']:
    return True
  elif len(date_list) == 1:
    return date_list[0] == date_int
  elif len(date_list) == 2:
    return  date_int >= date_list[0] and date_int <= date_list[1]
  return False

def as_timezone(dt, timezone):
  return localize(dt).astimezone(pytz.timezone(timezone))

def localize(dt):
  return pytz.utc.localize(dt)

def datetime_to_str(dt, format):
  return dt.strftime(format)

def str_to_datetime(str_dt,format):
  return localize(datetime.strptime(str_dt,format))

async def marcar_ponto(msg, target, date_list):
    now = as_timezone(datetime.now(),'America/Araguaina')
    data = datetime_to_str(now, "%d/%m/%Y")
    hora = datetime_to_str(now,"%H:%M:%S")
    author = f'{msg.author}'

    users = db['users']
    pontos = db['pontos']

    if author not in users.keys():
        users[author] = True
    else:
        users[author] = not users[author]

    marcacao = (author, f'{data} {hora}', users[author])

    pontos.append(marcacao)

    db['pontos'] = pontos
    db['users'] = users

    print(
        f'PONTO - Usuário {author} marcou ponto as {data} - {hora} de {"Entrada" if marcacao[2] else "Saida"}'
    )
    await msg.channel.send(
        f'PONTO - {author}: {data} - {hora} - {"Entrada" if marcacao[2] else "Saida"} - registrado'
    )


async def show_marcacoes(msg, target_list, date_list):
    pontos = db['pontos']
    lista_retorno = str()
    
    for target in target_list:
      for author, date_time, active in pontos:
        _date_time = str_to_datetime(date_time, "%d/%m/%Y %H:%M:%S")
        data = datetime_to_str(_date_time, '%d/%m/%Y')
        hora = datetime_to_str(_date_time, '%H:%M:%S')

        if is_all_or_equal(target,author) and date_list_controller(date_list,_date_time.date()):
          lista_retorno += f'LOG - {author} - {data} - {hora} - {"Entrada" if active else "Saida"}\n'
 
    print(
        f'CONSULTA - Usuário {msg.author} consultou o historico de {target_list} com as datas {[datetime_to_str(i,"%d/%m/%Y") for i in date_list] if date_list != ["All"] else date_list}'
    )
    try:
        await msg.channel.send(lista_retorno)
    except (errors.HTTPException):
        await msg.channel.send("CONSULTA - Nenhum registro encontrado 'o'")


async def reset(msg, *args):
    if msg.author.permissions_in(msg.channel).administrator:
        db['pontos'] = []
        db['users'] = []
        await msg.channel.send(
            f'RESET - Histórico de pontos apagados por {msg.author}')
        print(f'RESET - Histórico de pontos apagados por {msg.author}')
    else:
        await msg.channel.send(
            f'RESET - Opa! Você não tem permissão pra isso {msg.author}. Chame um adulto ou alguém responsável caso preciso muito. :p'
        )
        print(
            f'RESET - {msg.author} tentou apagar o historico de pontos mas não teve permissão.'
        )


async def help(msg, *args):
    await msg.channel.send(
        'COMANDOS:\n\n/ponto - Para marcar o seu ponto \n\n /consulta -  Consultar pontos. Podem ser expecificados usuários e datas para a consulta. \n Ex:  /consulta @usuário 01/01/2021 01/02/2021\n -Pode ter mais de um usuário\n -Com apenas um data vai buscar registros do dia em questão.\n -Com mais de uma data irá buscar por intervalo de tempo \n\n /help - Ajuda \n\n Site para checar se o bot está rodando: https://testebot.fullmetalcomuni.repl.co'
    )
    print(f'AJUDA - {msg.author} pediu ajuda')


def get_dates(msg):
    re_date = re.findall(r'\d{2}/\d{2}/\d{4}', msg)
    date_list = [
        datetime.strptime(i, '%d/%m/%Y').date()
        for i in re_date
    ]
    return date_list


commands = {
    '/ponto': marcar_ponto,
    '/consulta': show_marcacoes,
    '/reset': reset,
    '/help': help
}


@client.event
async def on_ready():
    print(f'{client.user} logged and ready')


@client.event
async def on_message(message, target=None, date_list=None):
    msg = message.content
    target = ['All']
    date_list = ['All']

    if message.mentions != []:
        target = [f'{i.name}#{i.discriminator}' for i in message.mentions]

    if get_dates(msg) != []:
        date_list = get_dates(msg)

    if message.author == client.user:
        return
    for i in commands.keys():
        if msg.startswith(i):
            await commands[i](message, target, date_list)

keep_alive()
client.run(token)
