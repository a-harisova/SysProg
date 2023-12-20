from msg import *
from tpl import *
cgitb.enable()

sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

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

def Load(user_id):
    SendMsg(user_id, MR_BROKER, MT_GETLAST)
    ms = Call(user_id, MR_BROKER, MT_GETDATA)
    if ms.Header.Type == MT_GETLAST and ms.Header.From == MR_BROKER:
        return ms.Data
    else:
        return ''

def main():
    form = cgi.FieldStorage()
    user_id = form.getvalue('hidden_id')
    if user_id is None:
        m = Call(MR_BROKER, 0,  MT_INIT)
        user_id = m.Header.To

        PrintHeader()
        PrintForm(user_id)
        PrintFooter()
        return
    else:
        user_id = int(user_id)

    menu = form.getvalue('menu')
    if menu == '1':
        to_id = form.getvalue('toclientid')
        msg = form.getvalue('getmessage')
        if msg is not None and to_id is not None and user_id is not None:
            SendMsg(user_id, int(to_id), MT_DATA, msg)

        PrintHeader()
        PrintForm(user_id)
        PrintFooter()
    elif menu == '2':
        msg = form.getvalue('getmessage')
        if msg is not None and user_id is not None:
            SendMsg(user_id, MR_ALL, MT_DATA, msg)

        PrintHeader()
        PrintForm(user_id)
        PrintFooter()
    elif menu == '3':
        PrintHeader()
        PrintForm(user_id, Load(user_id))
        PrintFooter()
    else:
        PrintHeader()
        PrintForm(user_id)
        PrintFooter()
        print('ОШИБКА! Выберите действие!<br>')

main()