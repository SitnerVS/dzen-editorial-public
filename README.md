# Публичная редакционная площадка

Публичная витрина материалов редакционного конвейера. Исходный код, API-ключи и внутренние данные остаются в закрытом репозитории `dzen-editorial-engine`.

## Сайт и RSS

- Сайт: https://sitnervs.github.io/dzen-editorial-public/
- RSS: https://sitnervs.github.io/dzen-editorial-public/feed.xml
- Sitemap: https://sitnervs.github.io/dzen-editorial-public/sitemap.xml

Адреса станут рабочими после включения GitHub Pages и успешного deployment.

## Локальная сборка

```bash
python -m pip install -r requirements.txt
python build_site.py
```

Результат создаётся в `_site/`.

## Публикация

GitHub Actions собирает статический сайт и RSS при каждом push в `main`. В GitHub Settings → Pages необходимо один раз выбрать Source: GitHub Actions.

## Важно

Наличие сайта и RSS не означает, что сайт принят Яндекс Дзен. Решение о подключении принимает платформа. Формат RSS включает RSS 2.0 и элементы Яндекса для полного текста; соответствие конкретным требованиям Дзена нужно подтвердить в интерфейсе Студии Дзена.
