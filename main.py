from discord import *
from replit import db
import pytz
from datetime import datetime
import json
import os

client = Client()
token = os.getenv('TOKEN')


async def marcar_ponto(msg):
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

    print(f'CONSOLE - Usuário {marcacao[0]} marcou ponto as {marcacao[1]} - {marcacao[2]} de {"Entrada" if marcacao[3] else "Saida"}')
    await msg.channel.send(f'PONTO - {author}: {data} - {hora} - {"Entrada" if marcacao[3] else "Saida"} - registrado')


async def show_all(msg):
  pontos = db['pontos']
  lista = str()
  for i,j,k,l in pontos:
    lista += f'LOG - {i} - {j} - {k} - {"Entrada" if l else "Saida"}\n'
  print(lista)
  await msg.channel.send(lista)

commands = {'/ponto': marcar_ponto, '/marcacoes': show_all}


@client.event
async def on_ready():
    print(f'User {client.user} logged')


@client.event
async def on_message(message):
    msg = message.content

    if message.author == client.user:
        return
    for i in commands.keys():
        if msg.startswith(i):
            await commands[i](message)


client.run(token)
