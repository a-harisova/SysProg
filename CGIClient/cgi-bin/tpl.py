import cgi, pickle, cgitb, codecs, sys, datetime, os, html
selfurl = os.environ['SCRIPT_NAME']
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

def PrintFormClient(user_id):
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
                        <option value="2">Отправить сообщение всем клиентам</option>
                        <option value="3">Вывести новое сообщение (при наличии)</option>
                      </select>
                    </div>
                  </div>
                </div>""")

def PrintFormSendClient(data = ''):
    print(f"""<div class = "center">
                  <h6>Ввведите ID клиента:</h6>
                  <textarea name=toclientid rows=1 cols=10 wrap=virtual ></textarea>
                  <textarea name=printmessage rows=10 cols=60 wrap=virtual disabled>{data}</textarea>
                  <textarea name=getmessage rows=1 cols=60 wrap=virtual ></textarea>
                  <input type="submit" value="Выполнить действие!">
                </div>""")

def PrintFormSendAll(data = ''):
    print(f"""<div class = "center">
                  <textarea name=printmessage rows=10 cols=60 wrap=virtual disabled>{data}</textarea>
                  <textarea name=getmessage rows=1 cols=60 wrap=virtual ></textarea>
                  <input type="submit" value="Выполнить действие!">
                </div>
              </form>
            </div>
          </main>""")

def PrintFormGet(data = ''):
    print(f"""<div class = "center">
                  <textarea name=printmessage rows=10 cols=60 wrap=virtual disabled>{data}</textarea>
                  <input type="submit" value="Выполнить действие!">
                </div>""")

def PrintFooter():
    print("""</form>
            </div>
          </main>
          </body>
        </html>""")