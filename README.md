

# Бот для компании BIM Limited.

## О проекте БИМЛТД
Чат-бот для компании **BIM Limite** - консьерж-сервиса в сфере предоставления полного спектра услуг по проектированию, поставке, монтажу и обслуживанию систем вентиляции, кондиционирования и увлажнения воздуха. Компания позиционирует себя как премиум-сервис, предлагающий индивидуальный подход к каждому клиенту, включая разработку решений под ключ для объектов любой сложности.

**Цели:** 

Основные функции чат-бота:

- **Запрос от клиента:** Пользователь (например, клиент, прораб или дизайнер) начинает диалог с чат-ботом, указывая свои потребности или интересующие системы.
- **Предоставление вариантов:** Чат-бот предлагает клиенту различные типы товаров (вентиляция, кондиционирование, увлажнение и т.д.) на основе введенной информации.
- **Фильтрация по характеристикам:** Клиент выбирает параметры (мощность, производительность, габариты, цена и т.д.), которые ему интересны.
- **Предложения по маркам:** На основе выбранных характеристик чат-бот предлагает список брендов и моделей, соответствующих запросу.
- **Предоставление PDF с информацией:** После выбора конкретной марки и модели клиент получает PDF-страницу из каталога с подробной технической информацией об этом товаре.
- **Сбор статистики по выбираемым клиентами моделям**.

Для удобства работы с базой данных, разработана административная панель. 
В качестве базы данных по умолчанию используется PostgreSQL.

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)
![Flask](https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white)
![Telegram](https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)
![Bootstrap](https://img.shields.io/badge/bootstrap-%238511FA.svg?style=for-the-badge&logo=bootstrap&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
![Nginx](https://img.shields.io/badge/nginx-%23009639.svg?style=for-the-badge&logo=nginx&logoColor=white)

## Основной стек разработки.

- Python 3.11,
- SQLAlchemy 2.0.30,
- PostgreSQL 13,
- Flask 3.0.3,
- Python-telegram-bot 21.4,
- Bootstrap 5.3.3,
- Docker 27.2.1

## Настройка и запуск проекта.
### 1. Запуск проект на локальном компьютере.
1.1. Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/Studio-Yandex-Practicum/bim_ltd_team_2.git
```

```
cd bim_ltd_team_2
```

1.2. Создать и активировать виртуальное окружение:

```
python3 -m venv venv
```

* Если у вас Linux/macOS:

    ```
    source venv/bin/activate
    ```

* Если у вас Windows:

    ```
    source venv/scripts/activate
    ```

1.3. Установить зависимости для проверки стиля
```shell
pip install -r requirements_style.txt
```

1.3.1. Настроить `pre-commit`

```shell
pre-commit install
```

1.3.2. Проверить, что `pre-commit` работает корректно

```shell
pre-commit run --all-files
```

Возможно потребуется запуск несколько раз. 
В итоге должен получиться примерно такой вывод:

```shell
trim trailing whitespace............Passed
fix end of files....................Passed
check yaml..........................Passed
check for added large files.........Passed
check for merge conflicts...........Passed
isort...............................Passed
flake8..............................Passed
black...............................Passed
```

1.4. Перейти в рабочую папку проекта:
```
cd src
```
**Далее все действия необходимо выполнять в данной папке.**

1.5. Установить зависимости из файла requirements.txt:
```
python3 -m pip install --upgrade pip
```
```
pip install -r requirements.txt
```
1.6. Создать в рабочей папке проекта (src) файл переменных окружения `.env` 
со следующими переменными:
```
BOT_TOKEN=               #Указать токен для телеграм-бота
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_DB=
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
SERVER_URL=               #Указать адрес ngrok сервера 
UVICORN_PORT=8000
UVICORN_SERVER=127.0.0.1
SECRET_KEY=               #Указать секретный ключ для flask
```
1.7. Установить [ngrok](https://ngrok.com/) по инструкции с сайта
и после получения адреса сервера, добавить его в файл переменных окружения 
`.env` - в переменную SERVER_URL

1.8. Применить миграции:
```
alembic upgrade head
```
1.9. Создать суперпользователя для управления базой данных:
```
python create_user.py имя_пользователя пароль_пользователя
```

1.10. Наполнить базу данных тестовыми данными (опционально):
```
python orm.py
```
1.11. Запустить проект:
```
python main.py
```
Бот и административная панель запускаются одновременно.

После запуска административная панель будет доступна по адресу,
указанному в переменной UVICORN_SERVER на порту, из переменной UVICORN_PORT,
например - http://127.0.0.1:8000/

### 2. Запуск проект в docker контейнерах.
2.1. Перейти в рабочую папку проекта:

```
cd src
```
**Далее все действия необходимо выполнять в данной папке.**

2.2. Создать в рабочей папке проекта (src) файл переменных окружения `.env`
со следующими переменными:
```
BOT_TOKEN=                #Указать токен для телеграм-бота
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_DB=              #Указать название docker котейнера с базой данных
POSTGRES_SERVER=
POSTGRES_PORT=5432
SERVER_URL=               #Указать сервер от ngrok
UVICORN_PORT=8000
UVICORN_SERVER=0.0.0.0    #Здесь необходимо указать именно так - 0.0.0.0
SECRET_KEY=               #Указать секретный ключ для flask
```
2.3. В папке gateway скорректировать файл nginx.conf
В строке "proxy_pass http://a1go3-backend-1:8000;" строку "a1go3-backend-1" 
заменить на название контейнера с бекендом проекта.

2.4. Выполнить команды:
```
docker compose build
```
```
docker compose up
```
2.5. Зайти в контейнер с бекендом проекта:
```
docker container exec -it <название контейнера> bash
```
и выполнить внутри этого контейнера команды:
```
alembic upgrade head
```
```
python create_user.py имя_пользователя пароль_пользователя
```
при желании наполнить тестовыми данными базу данных:
```
python orm.py
```
После запуска, адмиинистративная панель будет доступна по адресу: http://0.0.0.0:8000
