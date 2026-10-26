# Реестр категорий сайтов для Claude in Chrome

[English version](README.md) · [Страница реестра с проверкой за минуту](https://pr0t0be.github.io/claude-site-categories/) · [Прислать результат](#как-прислать-результат)

Открытый список: какой сайт в какой категории у Claude in Chrome (расширение Anthropic для Chrome). Категория определяет, как Claude ведёт себя на сайте: обычный сайт с кнопкой «Always allow», вопрос на каждое действие без возможности разрешить навсегда, или полная блокировка. Anthropic этот список не публикует. Здесь его собирают пользователи по своим наблюдениям, каждая строка с датой и способом проверки.

Реестр ведётся как пинг: открыли сайт, расширение спросило сервер Anthropic, сервер ответил категорией, ответ записали.

## Зачем

Перед действием на сайте расширение отправляет адрес страницы на сервер Anthropic и получает категорию. На сайтах категории category3 Claude спрашивает подтверждение на каждый клик, кнопка «Always allow» отключена, и режимы боковой панели («Automatically approve», «Skip all approvals») этого не меняют. Узнаёшь об этом только когда упёрся. Список позволяет узнать заранее, что ждёт на рабочем сайте или на сайте, который делаете для клиента.

## Как устроена проверка у Anthropic

По коду расширения Claude in Chrome версии 1.0.102 (файлы `assets/mcpPermissions-*.js` и `assets/sidepanel-*.js`, разбор 25.10.2026):

- Запрос: `POST https://api.anthropic.com/api/web/url_hash_check/browser_extension`, заголовок `Authorization: Bearer <токен входа>`, тело `{"url": "<адрес страницы>", "max_supported_category": 4}`.
- Ответ: `{"url": ..., "domain": ..., "category": ..., "org_policy": ..., "policy_source": ...}`. Поле `domain` показывает, что категория даётся на домен, а не на страницу.
- Кеш 5 минут на адрес (`CACHE_TTL_MS = 3e5`). Запрос уходит из служебного процесса (service worker) расширения, не со страницы.
- Списка сайтов в коде расширения нет. Категорию присылает сервер. Критерии Anthropic не публикует; в справке сказано только, что есть сайты, на которых Claude требует подтверждения на каждое действие, и что Claude спрашивает разрешение перед финансовыми сайтами.

| Категория | Что делает расширение |
|---|---|
| category0 | обычный сайт, «Always allow» работает |
| category4 | сайт с чужим контентом: один раз на домен окно «By continuing, you confirm you have the right to access content on this site», после подтверждения как обычный |
| category3 | вопрос на каждое действие: подсказка «You must approve any Claude action on this site», в окне разрешения надпись «Site-level permissions are disabled for this site», кнопка «Always allow» отключена |
| category2 | заблокирован без страницы blocked.html; назначение в коде не описано |
| category1 | заблокирован совсем, вкладка переводится на blocked.html |

Служебные значения, которые сервер не присылает, а расширение выставляет само: `category_unknown_error` (категорию получить не удалось, расширение блокирует «as a precaution») и `category_org_blocked` (сервер вернул `org_policy: "block"` или политика организации в Chrome). В реестр они не вносятся.

Порядок по строгости в коде: category0 < category4 < category3 < category_unknown_error < category2 = category_org_blocked < category1.

## Реестр

<!-- registry:start -->
_9 entries (category0: 2, category3: 7). Generated from registry.csv by validate.py, do not edit by hand._

| domain | category | checked_at | method | reporter | source | notes |
|---|---|---|---|---|---|---|
| fl.ru | category0 | 2026-10-22 | dialog_observed | pr0t0be | self-report (registry author; observed 2026-10-21..22) | Always allow button present and it worked on later actions |
| freelance.ru | category0 | 2026-10-22 | dialog_observed | pr0t0be | self-report (registry author; observed 2026-10-21..22) | Always allow button present and it worked on later actions |
| dev.vk.com | category3 | 2026-09-16 | third_party_report | anthropics/claude-code#94880 | [github.com/anthropics/claude-code/issues/94880](https://github.com/anthropics/claude-code/issues/94880) | Issue author: site-level permissions unavailable, no way to grant them; category inferred from the dialog, not from a server response |
| docs.avito.ru | category3 | 2026-10-02 | third_party_report | anthropics/claude-code#99007 | [github.com/anthropics/claude-code/issues/99007](https://github.com/anthropics/claude-code/issues/99007) | Issue author's conclusion from the extension code path (category3 from url_hash_check); no screenshot of the response |
| facebook.com | category3 | 2026-06-20 | third_party_report | abrahamjeyaraj.com | [www.abrahamjeyaraj.com/articles/claude-chrome-facebook-pe...](https://www.abrahamjeyaraj.com/articles/claude-chrome-facebook-permission-wall) | Blog post: permission prompt on every action, site-level permissions disabled; category inferred from the dialog |
| habr.com | category3 | 2026-10-26 | dialog_observed | pr0t0be | self-report (registry author; navigate-to dialog) | Dialog 'Claude wants to navigate to: habr.com' had no Always allow button and said Site-level permissions are disabled for this site; extension version not recorded |
| redash.k.avito.ru | category3 | 2026-10-02 | third_party_report | anthropics/claude-code#99007 | [github.com/anthropics/claude-code/issues/99007](https://github.com/anthropics/claude-code/issues/99007) | Issue author's conclusion from the extension code path (category3 from url_hash_check); no screenshot of the response |
| stash.msk.avito.ru | category3 | 2026-10-02 | third_party_report | anthropics/claude-code#99007 | [github.com/anthropics/claude-code/issues/99007](https://github.com/anthropics/claude-code/issues/99007) | Issue author's conclusion from the extension code path (category3 from url_hash_check); no screenshot of the response |
| www.avito.ru | category3 | 2026-10-25 | devtools_response | pr0t0be | [www.avito.ru_category3_2026-10-25.webp](evidence/www.avito.ru_category3_2026-10-25.webp) | Response tab of url_hash_check in the extension service worker DevTools; org_policy null, policy_source null; extension 1.0.102 |
<!-- registry:end -->

Исходник: [registry.csv](registry.csv). Таблица выше и [страница реестра](https://pr0t0be.github.io/claude-site-categories/) собираются из него скриптом `python validate.py`.

Колонки:

- `domain`: домен из поля `domain` ответа сервера, либо хост из адресной строки. Строчными буквами, без `https://` и пути.
- `category`: category0, category1, category2, category3 или category4.
- `checked_at`: дата наблюдения, ГГГГ-ММ-ДД. Обязательна: категория может измениться.
- `method`: как проверено. `devtools_response`: ответ сервера увиден в DevTools. `dialog_observed`: вывод по окну разрешения (есть или нет «Always allow», есть ли страница blocked). `third_party_report`: пересказ чужого публичного сообщения (issue, статья), категория выведена из описания.
- `reporter`: кто наблюдал (логин GitHub, `form` для ответов из формы) или откуда пересказ.
- `source`: ссылка на issue, статью или файл в папке `evidence/` (скриншот только вкладки Response или окна).
- `notes`: что ещё важно: текст окна, версия расширения, продукт (расширение или встроенный браузер Claude Desktop), оговорки.

Надёжность по убыванию: `devtools_response` > `dialog_observed` > `third_party_report`. Строка с `third_party_report` это не наблюдение участников реестра, а ссылка на чужое сообщение; Anthropic такие сообщения не подтверждала.

## Как проверить свой сайт

### За минуту, по виду окна

Нужен Chrome с расширением Claude. Откройте сайт, в панели Claude напишите: «Открой эту страницу и нажми любую безопасную ссылку в меню. Ничего не вводи и не отправляй». Смотрите на первое окно:

| Что увидели | Категория |
|---|---|
| Страница blocked, сайт не открылся | category1 (или блок политикой организации) |
| Окно с кнопкой «Always allow» | category0 |
| Окно без этой кнопки, внизу «Site-level permissions are disabled for this site» | category3 |
| Один раз окно «By continuing, you confirm you have the right to access content on this site», дальше как обычный | category4 |

Способ в реестре: `dialog_observed`.

### Точно, через DevTools, пять шагов

1. В Chrome откройте `chrome://extensions` и справа вверху включите «Режим разработчика».
2. В карточке расширения Claude нажмите ссылку «service worker» (мелкая, под описанием расширения). Откроются инструменты разработчика.
3. Перейдите на вкладку Network и в поле фильтра введите `url_hash`.
4. В панели Claude попросите открыть нужный сайт.
5. В списке появится строка `browser_extension`. Нажмите на неё и откройте вкладку Response: там поле `category`.

Если строки нет, ответ лежит в кеше 5 минут: попросите открыть другую страницу того же сайта.

**Предупреждение.** Во вкладке Headers рядом виден ваш токен входа в аккаунт Claude. Смотрите только Response. Скриншоты Headers не присылайте никому, реестр удаляет их не читая.

Способ в реестре: `devtools_response`.

## Как прислать результат

Три двери, выбирайте самую простую:

1. **Форма** ([открыть напрямую](https://docs.google.com/forms/d/e/1FAIpQLSfi7jWeiR1db45H7FNWV712p4t1Nm3f9PebTDT6ppyLhOnq_Q/viewform) или на [странице реестра](https://pr0t0be.github.io/claude-site-categories/#send)): без входа и без почты, вопросы на английском. Домен, что увидели, дата, какой продукт Claude, по желанию ссылка на скриншот, комментарий. (Тексты полей и как её собрать: [FORM_setup.md](FORM_setup.md).)
2. **Issue на GitHub** по шаблону «Report a site category»: для тех, у кого уже есть аккаунт GitHub.
3. **Pull request**: строка в `registry.csv`, скриншот в `evidence/` (имя `домен_категория_ГГГГ-ММ-ДД.webp` или `.png`), затем `python validate.py` и коммит вместе с обновлёнными README и `docs/registry.csv`.

Каждое сообщение просматривает человек, прежде чем оно попадёт в `registry.csv`. Подробнее в [CONTRIBUTING.md](CONTRIBUTING.md).

## Как пополняется реестр

Три потока, и ни один не обращается к эндпоинту Anthropic скриптом:

- **Сообщения людей** (форма, issue, pull request): главный поток. Ответы формы забирает `python import_form.py --url <ссылка на опубликованный CSV>` в `candidates_form.csv`, дальше ручной просмотр.
- **Радар по GitHub**: `python radar_github.py` ищет в открытых issue репозитория `anthropics/claude-code` фразы, которые сопровождают это поведение («Site-level permissions are disabled», «category3», «url_hash_check», «per-action approval»), вытаскивает домены рядом с ними с цитатой до 200 знаков и пишет `candidates_github.csv`, а список найденных issue в `candidates_github_issues.csv`. Обращается только к GitHub: через `gh`, если он установлен, иначе обычный REST без токена. Кандидатов просматривает человек и, если источник действительно описывает наблюдение, вносит как `third_party_report`. Запуск вручную или раз в день по планировщику, секретов нет.
- **Ручные сессии проверки**: человек работает с Claude in Chrome как обычно, рядом открыт DevTools служебного процесса, и записывает точный ответ сервера по списку сайтов. Первые 20 сайтов и порядок действий в [CHECKLIST_manual.md](CHECKLIST_manual.md). Повторять раз в месяц: категории могут меняться.

**Чего не делаем:** массовый автоматический опрос `url_hash_check`. Это недокументированный эндпоинт под личным токеном входа; прогон списка доменов через него рискует аккаунтом и условиями использования, такие строки не принимаются.

## Правила реестра

1. Только собственное наблюдение: ответ сервера или окно разрешения, с датой. Домысел по типу сайта («наверное, банк в category3») не принимается.
2. Массовое автоматическое сканирование через эндпоинт Anthropic не делаем и не просим.
3. Категория может меняться. Поэтому дата обязательна, а новое наблюдение того же домена добавляется отдельной строкой, старая не удаляется.
4. Скриншоты вкладки Headers удаляются не читая: там токен. Только Response или окно.
5. Домен записывается как в ответе сервера (`www.avito.ru`, а не `avito.ru`), поддомены отдельными строками.
6. Чужие публичные сообщения можно вносить как `third_party_report` со ссылкой, но без дорисовки деталей: только то, что написано в источнике.

## Файлы

| Файл | Что это |
|---|---|
| `registry.csv` | реестр, источник правды |
| `validate.py` | проверяет CSV, собирает таблицы в README, копирует CSV в `docs/`; `--check` в CI |
| `docs/index.html` | страница реестра для GitHub Pages (включить Pages из папки `docs/` ветки `main`) |
| `radar_github.py` | радар по issue GitHub, пишет `candidates_github.csv` и `candidates_github_issues.csv` |
| `import_form.py` | забирает ответы формы в `candidates_form.csv` |
| `FORM_setup.md` | поля формы и сборка за 5 минут |
| `CHECKLIST_manual.md` | порядок ручной сессии и первые 20 сайтов |
| `CONTRIBUTING.md` | как добавить строку |
| `evidence/` | скриншоты вкладки Response или окон, никогда Headers |
| `POST_reddit_draft.md` | черновик анонса |

## Чего реестр не знает

- Критерии, по которым Anthropic относит сайт к категории. Не опубликованы.
- Полный список. Здесь только то, что кто-то проверил.
- Проверяет ли встроенный браузер приложения Claude Desktop категории тем же запросом. По документации Anthropic он сверяется с тем же списком безопасности сайтов, но ответ сервера для него никто из участников не видел.
- Можно ли подать заявку на пересмотр категории. В документации не описано.

## Лицензии

Данные (`registry.csv`, `candidates_*.csv`, `evidence/`): [CC BY 4.0](LICENSE-DATA.md). Код: [MIT](LICENSE).

## Ссылки

- Справка Anthropic по разрешениям Claude in Chrome: https://support.claude.com/en/articles/12902446-claude-in-chrome-permissions-guide
- Справка «Use Claude in Chrome safely»: https://support.claude.com/en/articles/12902428-use-claude-in-chrome-safely
- Браузер в Claude Desktop для организаций, раздел Site safety check: https://claude.com/docs/third-party/claude-desktop/browser.md
- Claude Code с Chrome: https://code.claude.com/docs/en/chrome.md
- Обращения пользователей в репозитории Claude Code: [99007](https://github.com/anthropics/claude-code/issues/99007), [94880](https://github.com/anthropics/claude-code/issues/94880), [91495](https://github.com/anthropics/claude-code/issues/91495), [93201](https://github.com/anthropics/claude-code/issues/93201), [101684](https://github.com/anthropics/claude-code/issues/101684), [104074](https://github.com/anthropics/claude-code/issues/104074)

Реестр не связан с Anthropic. Названия Claude и Anthropic принадлежат их владельцу.
