import asyncio

HOST = 'localhost'
PORT = 9069

async def tcp_echo_client(host, port):
    reader, writer = await asyncio.open_connection(host, port)

    while True:
        data = await reader.read(1024)
        print(data.decode())
        message = input()
        writer.write(message.encode())
        await writer.drain()
        if message == 'exit' or data == '':
            data = await reader.read(18)
            print('Клиент отключён')
            writer.close()
            break

if __name__ == "__main__":
    asyncio.run(tcp_echo_client(HOST, PORT))
