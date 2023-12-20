import threading
from dataclasses import dataclass
import time, json,os
from msg import *

def Send(s, m):
    s.send(struct.pack(f'iiii', m.Header.To, m.Header.From, m.Header.Type, m.Header.Size))
    if m.Header.Size > 0:
        s.send(struct.pack(f'{m.Header.Size}s', m.Data.encode('cp866')))

def Receive(s, m):
    try:
        (m.Header.To, m.Header.From, m.Header.Type, m.Header.Size) = struct.unpack('iiii', s.recv(16))
    except:
        m.Header.Size = 0
        m.Header.Type = MT_NODATA
    if m.Header.Size > 0:
        m.Data = struct.unpack(f'{m.Header.Size}s', s.recv(m.Header.Size))[0].decode('cp866')

def SendMsg(From, To, Type=MT_DATA, Data=""):
    HOST = 'localhost'
    PORT = 12345
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        m = Message(To, From, Type, Data)
        Send(s, m)

def Call(From, To, Type=MT_DATA, Data=""):
    HOST = 'localhost'
    PORT = 12345
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        m = Message(To, From, Type, Data)
        Send(s, m)
        Receive(s, m)
        return m

def ProcessMessages(storage_id):
    while True:
        m = Call(storage_id, MR_BROKER, MT_GETDATA)
        if (m.Header.Type == MT_DATA):
            data = []
            try:
                with open('msgs.json', 'r') as f:
                    data = json.load(f)
                    print(data)
            except:
                with open('msgs.json', 'w') as f:
                    pass

            with open('msgs.json', 'w') as f:
                client, msg = m.Data.split('&')
                data.append({'to': m.Header.From, 'from': client, 'message': msg})
                print(data)
                json.dump(data, f)
                print(f"New msg added to {m.Header.From}. \n")

        if (m.Header.Type == MT_GETLAST):
            with open('msgs.json', 'r') as f:
                data = json.load(f)

            filtered_msg = [message for message in data if
                                 (message.get('to') == m.Header.From or message.get('to') == "ALL")]
            text = ''
            for msg in filtered_msg:
                text += "Получено сообщение от клиента " + msg['from'] + ": " + msg['message'] + "\n"
            text = text[:-1]
            Call(storage_id, m.Header.From, MT_GETLAST, text)
            print(f"Last msgs sent to {m.Header.From}: {text}. \n")
        else:
            time.sleep(1)

        
def Storage():
    m = Call(MR_BROKER, 0, MT_INITSTORAGE)
    storage_id = m.Header.To
    t = threading.Thread(target=ProcessMessages(storage_id), daemon = True)
    t.start()
    while(1):
        time.sleep(1)             
        
Storage()

