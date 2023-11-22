import sys
import threading
from dataclasses import dataclass
import socket, struct, time
from msg import *


@dataclass
class Client:
    id: int = 0

    def Send(self, s, m):
        s.send(struct.pack(f'iiii', m.Header.To, m.Header.From, m.Header.Type, m.Header.Size))
        if m.Header.Size > 0:
            s.send(struct.pack(f'{m.Header.Size}s', m.Data.encode('cp866')))

    def Receive(self, s, m):
        try:
            (m.Header.To, m.Header.From, m.Header.Type, m.Header.Size) = struct.unpack('iiii', s.recv(16))
        except:
            m.Header.Size = 0
            m.Header.Type = MT_NODATA
        if m.Header.Size > 0:
            m.Data = struct.unpack(f'{m.Header.Size}s', s.recv(m.Header.Size))[0].decode('cp866')

    def SendMsg(self, To, Type=MT_DATA, Data=""):
        HOST = 'localhost'
        PORT = 12345
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            m = Message(To, self.id, Type, Data)
            self.Send(s, m)

    def Call(self, To, Type=MT_DATA, Data=""):
        HOST = 'localhost'
        PORT = 12345
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            m = Message(To, self.id, Type, Data)
            self.Send(s, m)
            self.Receive(s, m)
            if m.Header.Type == MT_INIT:
                self.id = m.Header.To
            return m

    def ProcessMessages(self):
        while True:
            m = self.Call(MR_BROKER, MT_GETDATA)
            if m.Header.Type == MT_DATA:
                print("Получено сообщение от клиента:", m.Header.From)
                print(m.Data, "Выберите действие: ", sep='\n')
            elif m.Header.Type == MT_CHECKUSERS:
                print("Список клиентов:")
                print(m.Data, "Выберите действие: ", sep='\n')
            else:
                time.sleep(1)

    def PrintMenu(self):
        print("~Список действий~",
              "1. Отправить сообщение всем",
              "2. Отправить сообщение определенному юзеру",
              "3. Вывести всех клиентов",
              "4. Выход",
              "Выберите действие:", sep='\n')

    def MainFunction(self):
        print("Поздравляем с подключением! Ваш ID: ", self.id)
        while True:
            self.PrintMenu()
            x = int(input())
            if x == 1:
                print("Введите сообщение: ")
                msg = input()
                if msg is not None:
                    self.SendMsg(MR_ALL, MT_DATA, msg)
            elif x == 2:
                print("Введите ID клиента: ")
                clientID = int(input())
                print("Введите сообщение: ")
                msg = input()
                if msg is not None:
                    self.SendMsg(clientID, MT_DATA, msg)
            elif x == 3:
                self.SendMsg(MR_BROKER, MT_CHECKUSERS)
            elif x == 4:
                self.SendMsg(MR_BROKER, MT_EXIT)
                sys.exit("Сеанс окончен!")
            else:
                print("Ошибка! Попробуйте еще раз!")

    def __init__(self, id=0):
        m = self.Call(MR_BROKER, MT_INIT)
        t = threading.Thread(target=self.ProcessMessages)
        t.start()
        self.MainFunction()


client = Client()
