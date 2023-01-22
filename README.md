# Todolist project + Telegram bot

##### Web **[Сайт проекта](http://larin.ga/)**
##### Telegram **[Телеграм Бот](https://t.me/LaTodolistBot)**




1. Вход/регистрация/аутентификация через вк.
2. Создание целей.
3. Выбор временного интервала цели с отображением кол-ва дней до завершения цели.
4. Выбор категории цели (личные, работа, развитие, спорт и т. п.) с возможностью добавлять/удалять/обновлять категории.
5. Выбор приоритета цели (статичный список низкий, Средний и т. п.).
6. Выбор статуса выполнения цели:
- К выполнению
- В процессе
- Выполнено
- Архив
7. Изменение целей.
8. Изменение описания цели.
9. Изменение статуса.
10. Возможность менять приоритет и категорию у цели.
11. Удаление цели. При удалении цель меняет статус на «в архиве».
12. Поиск по названию цели.
13. Фильтрация по статусу, категории, приоритету, году.


### Stack

- Django
- Postgres
- Python
### Как запустить проект в среде разработки
- Создать виртуальную среду poetry install
- Установить зависимости poetry shell
- Установите переменные среды в .env file
- Создайте .env файл в папке todolist
- Вы можете скопировать переменные по умолчанию из todolist/.env.example
- docker-compose up -d
### Запустить проект
- перейти в папку todolist/ в которой есть docker-compose.yaml
- выполнить команду запуска контейнеров: sudo docker-compose up -d
- *** можно посмотреть статусы созданных контейнеров: sudo docker ps 

