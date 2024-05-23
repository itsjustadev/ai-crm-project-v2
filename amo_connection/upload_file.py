import requests
import io


def upload_file(url, file_path, max_chunk_size):
    with open(file_path, 'rb') as file:
        file_size = len(file.read())
        file.seek(0)  # Вернем указатель на начало файла

        chunk_number = 1
        returning_value = 0
        while True:
            chunk_data = file.read(max_chunk_size)
            if not chunk_data:
                break  # Если файл закончился, прекращаем цикл

            response = requests.post(url, data=chunk_data)

            if response.json().get('next_url'):
                url = response.json().get('next_url')
                print(f"Часть {chunk_number} загружена успешно.")
            else:
                returning_value = response.text
                print(response.text)
            chunk_number += len(chunk_data)
        if returning_value:
            return returning_value


def upload_file_without_download(url, file_content, max_chunk_size):
    file_size = len(file_content)

    chunk_number = 1
    offset = 0
    while offset < file_size:
        end_byte = offset + max_chunk_size
        chunk_data = file_content[offset:end_byte]

        response = requests.post(url, data=chunk_data)

        if response.json().get('next_url'):
            url = response.json().get('next_url')
            print(f"Часть {chunk_number} успешно загружена.")
        else:
            print(response.text)

        chunk_number += 1
        offset += max_chunk_size
