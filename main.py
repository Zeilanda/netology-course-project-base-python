import requests
import time
from progress.bar import IncrementalBar
from my_token import token_vk, token_ya
import json


class VkDownloader:
    def __init__(self, token):
        self.token = token

    def photos_download(self, user_id: str, amount: str):

        params = {'v': '5.131', 'access_token': {self.token}, 'owner_id': user_id, 'album_id': 'profile',
                  'extended': '1', 'photo_sizes': '1', 'count': amount}

        res = requests.get('https://api.vk.com/method/photos.get', params=params).json()
        info = res['response']['items']

        bar_download = IncrementalBar('Прогресс скачки фотографий:', max=len(info))

        photos_url_list = []
        for element in info:
            bar_download.next()

            photo_dict = {
                'file_name': f"{element['likes']['count']}_{element['id']}.jpg",
                'size': element['sizes'][-1]['type'],
                'url': element['sizes'][-1]['url']

            }
            photos_url_list.append(photo_dict)
            time.sleep(0.5)

        bar_download.finish()

        with open('json.txt', 'w') as file:
            json_data = json.dumps(photos_url_list, ensure_ascii=False, indent=3)
            file.write(json_data)

        return photos_url_list


class YaUploader:
    def __init__(self, token: str):
        self.token = token

    def create_folder(self, folder_name: str):
        """Метод создает папку на яндекс диске"""
        headers = {'Content-Type': 'application/json', 'Authorization': f'OAuth {self.token}'}
        url_folder = 'https://cloud-api.yandex.net/v1/disk/resources?path=' + folder_name
        requests.put(url_folder, headers=headers)
        check_folder = requests.get(url_folder, headers=headers)
        if check_folder.status_code == 200:
            print(f'Папка {folder_name} создана')
        else:
            print('Ошибка в создании папки')

    def upload(self, photo_list: list[dict], folder_name: str):
        """Метод загружает файлы по URL на яндекс диск"""
        bar_upload = IncrementalBar('Прогресс загрузки фотографий на Я.Диск:', max=len(photo_list))
        for photo_dict in photo_list:
            if 'file_name' and 'url' in photo_dict.keys():
                bar_upload.next()
                headers = {'Content-Type': 'application/json', 'Authorization': f'OAuth {self.token}'}
                file_path = folder_name + '/' + photo_dict['file_name']
                params = {'path': file_path, 'url': photo_dict['url']}
                url_file_upload = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
                requests.post(url_file_upload, headers=headers, params=params)
                time.sleep(1)

            else:
                print('Неверно сформированный json-файл')
        bar_upload.finish()

        headers = {'Content-Type': 'application/json', 'Authorization': f'OAuth {self.token}'}
        path = folder_name + '/json.txt'
        url = 'https://cloud-api.yandex.net/v1/disk/resources/upload?path=' + path
        json_to_download = requests.get(url, headers=headers).json()
        # print(f"link got: {json_to_download}")
        with open('json.txt', 'r') as file:
            json_file = file.read()
        try:
            resp = requests.put(json_to_download['href'], data=json_file)
            print(f"upload result: {resp}")
            return True
        except KeyError:
            print(json_to_download)
            return False


if __name__ == '__main__':
    owner_id = input('Введите идентификатор пользователя vkontakte: ')
    photos_amount = input('Введите количество скачиваемых фотографий (по умолчанию 50): ')
    folder = input('Введите название папки для фотографий на Я.Диске: ')
    downloader = VkDownloader(token_vk)
    photos_info = downloader.photos_download(owner_id, photos_amount)

    uploader = YaUploader(token_ya)
    uploader.create_folder(folder)
    uploader.upload(photos_info, folder)
