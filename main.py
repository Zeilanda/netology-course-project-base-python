import requests
import time
from progress.bar import IncrementalBar
from my_token import token_vk, token_ya


class VkDownloader:
    def __init__(self, token):
        self.token = token

    def photos_download(self, user_id: str):

        params = {'v': '5.131', 'access_token': {self.token}, 'owner_id': user_id, 'album_id': 'profile',
                  'extended': '1', 'photo_sizes': '1'}

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

    def upload(self, folder_name, file_name: str, file_url: str):
        """Метод загружает файлы по URL на яндекс диск"""
        headers = {'Content-Type': 'application/json', 'Authorization': f'OAuth {self.token}'}

        file_path = folder_name + '/' + file_name
        params = {'path': file_path, 'url': file_url}
        url_file_upload = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        requests.post(url_file_upload, headers=headers, params=params)
        print('Files uploaded')


if __name__ == '__main__':
    owner_id = input('Введите идентификатор пользователя vkontakte: ')
    folder = input('Введите название папки для фотографий на Я.Диске: ')
    downloader = VkDownloader(token_vk)
    photos_info = downloader.photos_download(owner_id)

    uploader = YaUploader(token_ya)
    uploader.create_folder(folder)
    bar_upload = IncrementalBar('Прогресс загрузки фотографий на Я.Диск:', max=len(photos_info))

    for photo_info in photos_info:
        bar_upload.next()
        uploader.upload(folder, photo_info['file_name'], photo_info['url'])
        time.sleep(1)

    bar_upload.finish()
