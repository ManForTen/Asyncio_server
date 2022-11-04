import asyncio
from hashlib import md5

HOST = 'localhost'
PORT = 9069
History = "History.txt"

async def auth(writer, reader, name):

    global clients
    print(name)
    if name in clients.keys():

        user_name = clients[name][0].decode()
        writer.write(f"Здравствуйте! {user_name}.\nВведите пароль:".encode())
        await writer.drain()

        while True:
            pas = await reader.read(100)
            h_pas = md5(pas).hexdigest()
            if h_pas == clients[name][1]:
                writer.write("Верный пароль!".encode())
                await writer.drain()
                break

            else:
                writer.write("Неверный пароль :(".encode())
                await writer.drain()
    else:
        writer.write("Здравствуйте, вы новый пользователь введите имя и пароль".encode())
        await writer.drain()
        writer.write("\nВведите свое имя: ".encode())
        await writer.drain()
        log = await reader.read(100)
        print(log)
        writer.write("\nВведите пароль:".encode())
        await writer.drain()
        pas = await reader.read(100)
        clients[name] = (log, md5(pas).hexdigest())
        print(clients)
        await writer.drain()

async def down(name, msg: str):
    with open(History, "a") as f:
        print(f"{name}>> {msg.decode()}", file = f)

async def chat(writer, reader, user, N):

    if N == '1':
        writer.write('Введите сообщение: '.encode())
        await writer.drain()
        msg = await reader.read(100)
        print(msg.decode())
        await down(user, msg)
        print(f"Получене сообщение {msg.decode()} от {user}")

    elif N == '2':
        with open(History, 'r') as f:
            for i in f:
                writer.write(i.encode())

    else:
        writer.write("Некорректный ввод".encode())
        await writer.drain()

async def handle_echo(reader, writer):
    global clients

    addr = writer.get_extra_info("peername")
    await auth(writer, reader, addr[0])

    writer.write("Введите число:\n1. Написать в общий чат. \n2. Посмотреть историю сообщений.\nДля выхода введите 'exit'.".encode())
    await writer.drain()

    par = await reader.read(4)
    par_d = par.decode()
    while par_d != "exit":
        par_d = par.decode()
        await chat(writer, reader, clients[addr[0]][0].decode(), par_d)
        writer.write("Введите число:\n1. Написать в общий чат. \n2. Посмотреть историю сообщений.\nДля выхода введите 'exit'.".encode())
        par = await reader.read(200)
    writer.close()

async def main():
    server = await asyncio.start_server(handle_echo, HOST, PORT)
    print('Сервер запущен с ',server.sockets[0].getsockname())
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    clients = {}
    asyncio.run(main())