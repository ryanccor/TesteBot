from discord import *
from replit import db
import pytz
import re
from datetime import datetime
import os

client = Client()
token = os.getenv('TOKEN')


async def marcar_ponto(msg, target, date_list):
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
        f'PONTO - Usuário {marcacao[0]} marcou ponto as {marcacao[1]} - {marcacao[2]} de {"Entrada" if marcacao[3] else "Saida"}'
    )
    await msg.channel.send(
        f'PONTO - {author}: {data} - {hora} - {"Entrada" if marcacao[3] else "Saida"} - registrado'
    )


async def show_marcacoes(msg, target, date_list):
    pontos = db['pontos']
    lista_retorno = str()

    if target is None:
        for i, j, k, l in pontos:
            if date_list is None:
                lista_retorno += f'LOG - {i} - {j} - {k} - {"Entrada" if l else "Saida"}\n'
            elif len(date_list) == 1:
                if j == date_list[0]:
                    lista_retorno += f'LOG - {i} - {j} - {k} - {"Entrada" if l else "Saida"}\n'
            elif len(date_list) == 2:
                if j >= date_list[0] and j <= date_list[1]:
                    lista_retorno += f'LOG - {i} - {j} - {k} - {"Entrada" if l else "Saida"}\n'
    else:
        for h in target:
            for i, j, k, l in pontos:
                if h == i:
                    if date_list is None:
                        lista_retorno += f'LOG - {i} - {j} - {k} - {"Entrada" if l else "Saida"}\n'
                    elif len(date_list) == 1:
                        if j == date_list[0]:
                            lista_retorno += f'LOG - {i} - {j} - {k} - {"Entrada" if l else "Saida"}\n'
                    elif len(date_list) == 2:
                        if j >= date_list[0] and j <= date_list[1]:
                            lista_retorno += f'LOG - {i} - {j} - {k} - {"Entrada" if l else "Saida"}\n'

    print(
        f'CONSULTA - Usuário {msg.author} consultou o historico de {target} com as datas {date_list}'
    )
    try:
        await msg.channel.send(lista_retorno)
    except (errors.HTTPException):
        await msg.channel.send("CONSULTA - Nenhum registro encontrado 'o'")


async def reset(msg, *args):
    if msg.author.permissions_in(msg.channel).administrator:
        db['pontos'] = []
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
        'COMANDOS:\n\n/ponto - Para marcar o seu ponto \n\n /consulta -  Consultar pontos. Podem ser expecificados usuários e datas para a consulta \n Ex:  /consulta @usuário 01/01/2021 01/02/2021 \n\n /help - Ajuda'
    )
    print(f'AJUDA - {msg.author} pediu ajuda')


def get_dates(msg):
    re_date = re.findall(r'\d{2}/\d{2}/\d{4}', msg)
    date_list = [
        datetime.strptime(i, '%d/%m/%Y').date().strftime("%d/%m/%Y")
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

    if message.mentions != []:
        target = [f'{i.name}#{i.discriminator}' for i in message.mentions]

    if get_dates(msg) != []:
        date_list = get_dates(msg)

    if message.author == client.user:
        return
    for i in commands.keys():
        if msg.startswith(i):
            await commands[i](message, target, date_list)


client.run(token)
