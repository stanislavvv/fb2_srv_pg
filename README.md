# fb2_srv postgres

NIH-проект

Сиё есть сервер opds для кучи fb2 в нескольких zip. Первоначальный проект fb2_srv_pseudostatic предназначался для запуска на одноплатниках и БД не использовал.

## Запуск постгреса для тех, кто не в курсе

Те, кто в курсе, как обращаться с постгресом -- вы и так в курсе, как создать базу и как обеспечить к ней доступ, можно раздел не читать, просто правильно заполните поля `PG_*` в `app/config.py`

Если устраивает постгрес в докере и на 127.0.0.1:5432 — правим файл `docker-compose.yml` по вкусу (например, пароль свой):

```
mkdir -p pgdata
docker-compose up -d
```

Очистка данных (сумели-таки запороть базу, залезши кривыми руками):

```
docker-compose down
sudo rm -rf pgdata
```

Если не править `docker-compose.yml`, то `PG_*` в `app/config.py` находятся в нужном состоянии

## Заполнение/обновление базы:

0) `./datachew.py lists` -- перегенерируем все списки книг с нуля (первоначальный запуск)
1) `./datachew.py new_lists` -- перегенерируем списки только для изменившихся архивов (дата архива новей, чем список)
2) `./datachew.py fillonly` -- новые книги из списков кладём в базу, старые не обновляем

При обновлении списка .zip (пришли новые, добавились книги в старые) - повторяем пункты 1 и 2.

После обновления можно сделать `gzip *.list` для уменьшения занимаемого места.

Если по какой-то причине требуется обновить книги (например, вы добавили туда кастомное описание в `file.zip.replace`), то вместо п.2:

```
./datachew.py fillall
```

## Запуск сервиса

  * Тестовый запуск: `opds.py` (можно добавить переменную окружения `FLASK_ENV=prod`, если требуется убедиться, что конфиг для прода верен)
  * Прод: `gunicorn.sh` (редактируйте по вкусу, там будет слушать на 0.0.0.0:8000)

Также есть `fb2_srv.service` для употребления с systemd, требует редактирования по месту.

