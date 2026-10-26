# Как внести запись / How to contribute

Русский ниже, English first.

## English

### What is accepted

- Your own observation on your own Claude account: the `url_hash_check` response seen in DevTools (`devtools_response`) or the permission dialog (`dialog_observed`).
- A public report by someone else (GitHub issue, blog post) as `third_party_report`, with a link, recorded exactly as the source says it. Do not add details the source does not contain.

### What is not accepted

- Results of automated scanning through `api.anthropic.com/api/web/url_hash_check/browser_extension`. It is an undocumented endpoint behind a personal login token. We do not run scans and we do not ask anyone to.
- Screenshots or pastes of the DevTools Headers tab: they contain the `Authorization: Bearer` token. Response tab only. If you attached Headers by mistake, delete the attachment and revoke your session (sign out of Claude everywhere).
- Guesses: "it is a bank, so it must be category3".
- Rows without a date.

### Option A: issue

Open an issue with the "Report a site category" template and fill in domain, category, date, method. A maintainer adds the row and links the issue in `source`.

### Option B: pull request

1. Add a row to `registry.csv`. Columns: `domain,category,checked_at,method,reporter,source,notes`.
   - `domain`: lowercase, no scheme, no path; as returned in the `domain` field if you have the response.
   - `category`: one of category0, category1, category2, category3, category4.
   - `checked_at`: YYYY-MM-DD.
   - `method`: devtools_response, dialog_observed or third_party_report.
   - `reporter`: your GitHub login, or the source name for third-party reports.
   - `source`: a URL, or `evidence/<file>` for your screenshot.
   - `notes`: free text in double quotes if it contains commas.
2. If you have a Response-tab screenshot, put it in `evidence/` as `domain_category_YYYY-MM-DD.webp` (or `.png`). Check it does not show the Headers tab or any token.
3. Run `python validate.py`. It checks the CSV and regenerates the tables in `README.md` and `README.en.md`. Commit the CSV, the evidence file and both README files together.
4. A new observation of a domain already in the list is a new row, not an edit of the old one.

CI runs `python validate.py --check` on every pull request.

## Русский

### Что принимается

- Собственное наблюдение на своём аккаунте Claude: ответ `url_hash_check`, увиденный в DevTools (`devtools_response`), или окно разрешения (`dialog_observed`).
- Чужое публичное сообщение (issue на GitHub, статья) как `third_party_report`, со ссылкой и ровно так, как написано в источнике. Детали, которых в источнике нет, не дописывать.

### Что не принимается

- Результаты автоматического сканирования через `api.anthropic.com/api/web/url_hash_check/browser_extension`. Это недокументированный эндпоинт под личным токеном входа. Сканирование не делаем и не просим.
- Скриншоты и копии вкладки Headers из DevTools: там токен `Authorization: Bearer`. Только вкладка Response. Если приложили Headers по ошибке, удалите вложение и выйдите из Claude на всех устройствах, чтобы токен перестал действовать.
- Догадки: «это банк, значит category3».
- Строки без даты.

### Вариант А: issue

Откройте issue по шаблону «Report a site category»: домен, категория, дата, способ. Сопровождающий добавит строку и укажет ссылку на issue в `source`.

### Вариант Б: pull request

1. Добавьте строку в `registry.csv`. Колонки: `domain,category,checked_at,method,reporter,source,notes`.
   - `domain`: строчными, без схемы и пути; как в поле `domain` ответа, если ответ есть.
   - `category`: category0, category1, category2, category3 или category4.
   - `checked_at`: ГГГГ-ММ-ДД.
   - `method`: devtools_response, dialog_observed или third_party_report.
   - `reporter`: ваш логин GitHub, для чужих сообщений название источника.
   - `source`: ссылка, либо `evidence/<файл>` для вашего скриншота.
   - `notes`: свободный текст, в двойных кавычках, если есть запятые.
2. Скриншот вкладки Response положите в `evidence/` с именем `домен_категория_ГГГГ-ММ-ДД.webp` (или `.png`). Проверьте, что на нём нет вкладки Headers и токена.
3. Запустите `python validate.py`. Скрипт проверит CSV и пересоберёт таблицы в `README.md` и `README.en.md`. Коммитьте CSV, файл из `evidence/` и оба README вместе.
4. Новое наблюдение домена, который уже есть в списке, это новая строка, а не правка старой.

CI запускает `python validate.py --check` на каждом pull request.
