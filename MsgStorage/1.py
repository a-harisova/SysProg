import json

def add_data_to_json(file_path, new_data):
    try:
        # Загружаем существующие данные из файла, если он существует
        with open(file_path, 'r') as json_file:
            existing_data = json.load(json_file)
    except FileNotFoundError:
        # Если файл не найден, создаем пустой список
        existing_data = []

    # Добавляем новые данные к существующим
    existing_data.append(new_data)

    # Записываем обновленные данные обратно в файл
    with open(file_path, 'w') as json_file:
        json.dump(existing_data, json_file)

def get_messages(file_path, requested_key, requested_value, from_value):
    try:
        # Загружаем существующие данные из файла, если он существует
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)
    except FileNotFoundError:
        # Если файл не найден, возвращаем пустой список
        data = []

    # Фильтруем сообщения по указанным ключу и значению
    filtered_messages = [message for message in data if
                         (message.get(requested_key) == requested_value or requested_value == "ALL") and
                         (message.get("from") == from_value or from_value == "ALL")]

    return filtered_messages

# Пример использования
new_data = {
    "to": 107,
    "from": 101,
    "message": "Hi, 107!"
}

#add_data_to_json("data.json", new_data)

# Запрос пользователя
requested_key = input("Введите ключ ('to' или 'from'): ")
requested_value = int(input("Введите значение: "))
from_value = input("Введите отправителя ('ALL' для всех): ")

# Получаем и выводим сообщения, соответствующие запросу
result_messages = get_messages("data.json", requested_key, requested_value, from_value)

print(f"Сообщения с {requested_key} = {requested_value} от {from_value}:")
for message in result_messages:
    print(message["message"])