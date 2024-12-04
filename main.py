import requests
from bs4 import BeautifulSoup
import pandas as pd


def find_missing_images():
    missing_images = []

    # Пройдемся по страницам с 1 по 16
    for page in range(1, 17):
        url = f"https://upravdom.com/kraski/?PAGEN_1={page}&ajax_mode=y&categorySort=popular&catalogUpravdomFilterArray_548_MIN=70&catalogUpravdomFilterArray_548_MAX=7079.63"

        response = requests.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Найдем все элементы с классом productPreview__imageWrapper
            product_wrappers = soup.find_all(class_='productPreview__imageWrapper')

            # Проверим каждое изображение
            for wrapper in product_wrappers:
                img = wrapper.find('img')
                if img is None or 'src' not in img.attrs or not img['src']:
                    # Если изображения нет, добавим ссылку на товар в список
                    product_link = wrapper.find_parent('a')['href']
                    missing_images.append(product_link)
        else:
            print(f"Ошибка при получении страницы {page}: {response.status_code}")

    return missing_images


def extract_descriptions(file_path):
    # Загрузим данные из Excel
    df = pd.read_excel(file_path)
    descriptions_list = []

    # Переберем строки DataFrame
    for index, row in df.iterrows():
        link = row.iloc[0]  # Первая колонка
        src_value = row.iloc[1]  # Вторая колонка

        # Проверяем значение во второй колонке
        if src_value == 'src="/local/templates/delement"':
            try:
                response = requests.get(link)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    # Ищем все <div> с классом productTitle__descriptionCode
                    descriptions = soup.find_all('div', class_='productTitle__descriptionCode')

                    # Сохраняем текст каждого найденного <div> в список
                    for desc in descriptions:
                        span_text = desc.get_text(strip=True)
                        descriptions_list.append(span_text)
                else:
                    print(f"Ошибка при получении страницы {link}: {response.status_code}")
            except Exception as e:
                print(f"Ошибка при обработке {link}: {e}")

    # Создаем DataFrame из списка описаний
    descriptions_df = pd.DataFrame(descriptions_list, columns=['Descriptions'])
    return descriptions_df


# Основная логика скрипта
if __name__ == "__main__":
    missing_images = find_missing_images()

    # Выведем все ссылки на товары без изображений
    for link in missing_images:
        print(link)

    # Путь к файлу Excel с данными
    file_path = '/Users/tsedilkin/Desktop/Краски.xlsx'  # Замените на свой путь к файлу
    descriptions_df = extract_descriptions(file_path)

    # Сохраняем DataFrame в новый Excel файл
    output_file_path = 'output_descriptions.xlsx'  # Укажите желаемое имя выходного файла
    descriptions_df.to_excel(output_file_path, index=False)

    print(f"Содержимое успешно сохранено в {output_file_path}")
