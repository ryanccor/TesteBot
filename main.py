from discord import *
from replit import db
import pytz
from datetime import datetime
import json
import os

client = Client()
token = os.getenv('TOKEN')


async def marcar_ponto(msg, args):
    now_utc = pytz.utc.localize(datetime.now())
    now = now_utc.astimezone(pytz.timezone('America/Araguaina'))
    data = now.strftime("%d/%m/%Y")
    hora = now.strftime("%H:%M:%S")
    author = f'{msg.author}'

    users = db['users']
    pontos = db['pontos']

    if author not in users.keys():
        users[author] = True
    else:
        users[author] = not users[author]

    marcacao = (author, data, hora, users[author])

    pontos.append(marcacao)

    db['pontos'] = pontos
    db['users'] = users

    print(
        f'CONSOLE - Usuário {marcacao[0]} marcou ponto as {marcacao[1]} - {marcacao[2]} de {"Entrada" if marcacao[3] else "Saida"}'
    )
    await msg.channel.send(
        f'PONTO - {author}: {data} - {hora} - {"Entrada" if marcacao[3] else "Saida"} - registrado'
    )


async def show_all_pontos(msg, args):
    pontos = db['pontos']
    lista = str()
    for i, j, k, l in pontos:
        lista += f'LOG - {i} - {j} - {k} - {"Entrada" if l else "Saida"}\n'
    print(lista)
    await msg.channel.send(lista)


async def get_by_id(msg, args):
  pass

commands = {
    '/ponto': marcar_ponto,
    '/all': show_all_pontos,
    '/consulta': get_by_id
}


@client.event
async def on_ready():
    print(f'User {client.user} logged')


@client.event
async def on_message(message, target = None):    
    msg = message.content.split()

    if len(msg) > 1:
      target = msg[1]
      print(target)
    if message.author == client.user:
        return
    for i in commands.keys():
        if msg[0].startswith(i):
            await commands[i](message, target)


client.run(token)
