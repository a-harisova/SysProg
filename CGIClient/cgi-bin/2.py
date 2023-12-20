import cgi, pickle, cgitb, codecs, sys, datetime, os, html
from msg import *
cgitb.enable()

sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
selfurl = os.environ['SCRIPT_NAME']

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
    m = Call(user_id, MR_BROKER, MT_GETDATA)
    if m.Header.Type == MT_DATA:
        return "Получено сообщение от клиента %d: %s \n" % (m.Header.From, m.Data)
    else:
        return ''

def PrintHeader():
    print("Content-type: text/html\n")
    print("""<!DOCTYPE html>
                <html lang="ru">
                <head>
                  <meta charset="UTF-8">
                  <title>MESSANGER</title>
                  <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css" integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous">
                  <style>
                    .consoles {
                    width:440px;
                    text-align:center
                    }
                    .center {
                    text-align:center
                    }
                  </style>
                </head>
            <body>
            <header class="container mt-3">
                <nav class="navbar navbar-expand-lg navbar-light bg-light">
                  <a class="navbar-brand" href="#">MESSANGER</a>
                  <span class="navbar-text d-sm-none d-lg-block">
                    ☺️
                  </span>
                </nav>
              </header>
              <main class="container mt-5">
                <div class="col-12 col-sm-10 col-lg-6 offset-lg-3 offset-sm-1">""")

def PrintForm(user_id, data = ''):
    print(f"""<form class="card mb-5" id="messageForm" action="{selfurl}" method="post">
                <div class="card-body text-center pt-2">
                  <h2 class="h4 card-title">{user_id} </h2>
                  <input type='hidden' name='hidden_id_field' value='{user_id}'>
                  <h3 class="h4 card-title">Напишите сообщение другим клиентам!</h3>
                  <div class="row">
                    <div class="col mb-2">
                      <select class = "consoles" name='menu'>
                        <option value="0">--Пожалуйста, выберите действие--</option>
                        <option value="1">Отправить сообщение клиенту</option>
                        <option value="2">Вывести новое сообщение (при наличии)</option>
                      </select>
                    </div>
                  </div>
                </div>
                <div class = "center">
                  <h6>Ввведите ID клиента:</h6>
                  <textarea name=toclientid rows=1 cols=10 wrap=virtual ></textarea>
                  <textarea name=printmessage rows=10 cols=60 wrap=virtual disabled>{data}</textarea>
                  <textarea name=getmessage rows=1 cols=60 wrap=virtual ></textarea>
                  <input type="submit" value="Выполнить действие!">
                </div>
              </form>
            </div>
          </main>""")

def PrintFooter():
    print("""</body>
        </html>""")

def main():
    form = cgi.FieldStorage()
    user_id = form.getvalue('hidden_id_field')
    if user_id is None:
        m = Call(MR_BROKER, 0,  MT_INIT)
        user_id = m.Header.To

        PrintHeader()
        PrintForm(user_id)
        PrintFormClient(user_id)
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
        PrintHeader()
        data = Load(user_id)
        PrintForm(user_id, data)
        PrintFooter()
    else:
        PrintHeader()
        PrintForm(user_id)
        PrintFooter()
        print('ОШИБКА! Выберите действие!<br>')


main()