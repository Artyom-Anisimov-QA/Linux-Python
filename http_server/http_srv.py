import socket
import datetime
from http import HTTPStatus

end_of_stream = '\r\n\r\n' # End receive data


# Парсим HTTP-запрос и извлекаем метод, путь, заголовки и параметры.
def parse_request(request):
    lines = request.split('\r\n')
    method, path, _ = lines[0].split(' ')
    headers = {}
    for line in lines[1:]:
        if ': ' in line:
            key, value = line.split(': ', 1)
            headers[key] = value
    return method, path, headers


# Обрабатываем входящее соедиение от клиента
def handle_client(connection):
    client_data = ''
    with connection:
        while True:
            data = connection.recv(1024)
            '''Данные от клиента принимаются порциями по 1024 байта
            (или меньше, если клиент отправил меньше данных.'''
            print("Received", data)
            if not data:
                break
            client_data += data.decode()
            '''Декодируем данные из байтов в строку и записываем в переменную'''
            if end_of_stream in client_data:
                break

        method, path, headers = parse_request(client_data)


        # Извлекаем статус из параметра status
        status_code = 200  # По умолчанию
        if '?' in path:
            path, params = path.split('?', 1)
            params = params.split('&')
            for param in params:
                if param.startswith('status='):
                    try:
                        status_code = int(param.split('=')[1])
                        if status_code not in HTTPStatus:
                            status_code = 200
                    except ValueError:
                        status_code = 200

        # Получаем фразу статуса
        status_phrase = HTTPStatus(status_code).phrase

        # Создаём ответ
        response_headers = {
            'Server': 'My_HTTP_Server',
            'Date': datetime.datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT'),
            'Content-Type': 'text/html; charset=UTF-8',
        }

        # Формируем тело ответа
        response_body = (
            f"Request Method: {method}\r\n"
            f"Request Source: {connection.getpeername()}\r\n"
            f"Response Status: {status_code} {status_phrase}\r\n"
        )
        for key, value in headers.items():
            response_body += f"{key}: {value}\r\n"

        # Формируем HTTP-ответ
        http_response = (
                f"HTTP/1.0 {status_code} {status_phrase}\r\n"
                + ''.join(f"{key}: {value}\r\n" for key, value in response_headers.items())
                + "\r\n"
                + response_body
        )

        # Отправляем ответ клиенту
        connection.send(http_response.encode())

        # Отправляем текущее серверное время клиенту
        serverTimeNow = "%s"%datetime.datetime.now()
        connection.send(http_response.encode()
                        + serverTimeNow.encode()
                        + f"\r\n".encode()
                        )


with socket.socket() as serverSocket:
    # Сбиндить tcp-сокет к IP-адресу и порту
    serverSocket.bind(("127.0.0.1", 40404))
    # Продолжаем слушать
    serverSocket.listen()

    while True: #Продолжаем принимать сообщения от клиентов.
        (clientConnection, clientAddress) = serverSocket.accept()
        handle_client(clientConnection)
        print(f"Sent data to {clientAddress}")