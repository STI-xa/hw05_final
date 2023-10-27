![image](https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue)
![image](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=green)
![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white)
![image](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)
![Bootstrap](https://img.shields.io/badge/bootstrap-%238511FA.svg?style=for-the-badge&logo=bootstrap&logoColor=white)
![HTML5](https://ziadoua.github.io/m3-Markdown-Badges/badges/HTML/html1.svg)
![CSS](https://ziadoua.github.io/m3-Markdown-Badges/badges/CSS/css1.svg)
# Проект Yatube

## Описание

*Yatube* - это социальная сеть с авторизацией, персональными лентами, комментариями и подписками на авторов статей.
___
## Функционал:
* Регистрируется и восстанавливается доступ по электронной почте;
* Добавляются изображения к посту;
* Создаются и редактируются собственные записи;
* Просмотриваются страницы других авторов;
* Комментируются записи других авторов;
* Подписки и отписки от авторов;
* Записи назначаются в отдельные группы;
* Личная страница для публикации записей;
* Отдельная лента с постами авторов на которых подписан * пользователь;
* Через панель администратора модерируются записи, происходит * управление пользователями и создаются группы.

### Зарегистрированные пользователи могут:

* Просматривать, публиковать, удалять и редактировать свои публикации;
* Просматривать, информацию о сообществах;
* Просматривать, публиковать комментарии от своего имени к публикациям других пользователей (включая самого себя), удалять и редактировать свои комментарии;
* Подписываться на других пользователей и просматривать свои подписки.
* 
### Анонимные пользователи могут:

* Просматривать, публикации;
* Просматривать, информацию о сообществах;
* Просматривать, комментарии;
____

## Установка:
Клонировать репозиторий:

```
git clone https://github.com/STI-xa/hw05_final
```

Перейти в папку с проектом:

```
cd hw05_final/
```

Установить виртуальное окружение для проекта:

```
python -m venv venv
```

Активировать виртуальное окружение для проекта:

*для OS Lunix и MacOS*
```
source venv/bin/activate
```


*для OS Windows*
```
source venv/Scripts/activate
```

Установить зависимости:
```
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Выполнить миграции:
```
cd yatube
python3 manage.py makemigrations
python3 manage.py migrate
```

Запустить проект локально:

```
python manage.py runserver
```


Зарегистирировать суперпользователя Django:
```
python manage.py createsuperuser
```


Набор доступных адресов:

'posts/' - отображение постов и публикаций.

'posts/{id}' - Получение, изменение, удаление поста с соответствующим id.

'posts/{post_id}/comments/' - Получение комментариев к посту с соответствующим post_id и публикация новых комментариев.

'posts/{post_id}/comments/{id}' - Получение, изменение, удаление комментария с соответствующим id к посту с соответствующим post_id.

'posts/groups/' - Получение описания зарегестрированных сообществ.

'posts/groups/{id}/' - Получение описания сообщества с соответствующим id.

'posts/follow/' - Получение информации о подписках текущего пользователя, создание новой подписки на пользователя.
