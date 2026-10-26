# Реестр категорий сайтов для Claude in Chrome

[English version](README.en.md)

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
_8 entries (category0: 2, category3: 6). Generated from registry.csv by validate.py, do not edit by hand._

| domain | category | checked_at | method | reporter | source | notes |
|---|---|---|---|---|---|---|
| fl.ru | category0 | 2026-10-22 | dialog_observed | pr0t0be | self-report (registry author; observed 2026-10-21..22) | Always allow button present and it worked on later actions |
| freelance.ru | category0 | 2026-10-22 | dialog_observed | pr0t0be | self-report (registry author; observed 2026-10-21..22) | Always allow button present and it worked on later actions |
| dev.vk.com | category3 | 2026-09-16 | third_party_report | anthropics/claude-code#94880 | [github.com/anthropics/claude-code/issues/94880](https://github.com/anthropics/claude-code/issues/94880) | Issue author: site-level permissions unavailable, no way to grant them; category inferred from the dialog, not from a server response |
| docs.avito.ru | category3 | 2026-10-02 | third_party_report | anthropics/claude-code#99007 | [github.com/anthropics/claude-code/issues/99007](https://github.com/anthropics/claude-code/issues/99007) | Issue author's conclusion from the extension code path (category3 from url_hash_check); no screenshot of the response |
| facebook.com | category3 | 2026-06-20 | third_party_report | abrahamjeyaraj.com | [www.abrahamjeyaraj.com/articles/claude-chrome-facebook-pe...](https://www.abrahamjeyaraj.com/articles/claude-chrome-facebook-permission-wall) | Blog post: permission prompt on every action, site-level permissions disabled; category inferred from the dialog |
| redash.k.avito.ru | category3 | 2026-10-02 | third_party_report | anthropics/claude-code#99007 | [github.com/anthropics/claude-code/issues/99007](https://github.com/anthropics/claude-code/issues/99007) | Issue author's conclusion from the extension code path (category3 from url_hash_check); no screenshot of the response |
| stash.msk.avito.ru | category3 | 2026-10-02 | third_party_report | anthropics/claude-code#99007 | [github.com/anthropics/claude-code/issues/99007](https://github.com/anthropics/claude-code/issues/99007) | Issue author's conclusion from the extension code path (category3 from url_hash_check); no screenshot of the response |
| www.avito.ru | category3 | 2026-10-25 | devtools_response | pr0t0be | [www.avito.ru_category3_2026-10-25.webp](evidence/www.avito.ru_category3_2026-10-25.webp) | Response tab of url_hash_check in the extension service worker DevTools; org_policy null, policy_source null; extension 1.0.102 |
<!-- registry:end -->

Исходник: [registry.csv](registry.csv). Таблица выше собирается из него скриптом `python validate.py`.

Колонки:

- `domain`: домен из поля `domain` ответа сервера, либо хост из адресной строки. Строчными буквами, без `https://` и пути.
- `category`: category0, category1, category2, category3 или category4.
- `checked_at`: дата наблюдения, ГГГГ-ММ-ДД. Обязательна: категория может измениться.
- `method`: как проверено. `devtools_response`: ответ сервера увиден в DevTools. `dialog_observed`: вывод по окну разрешения (есть или нет «Always allow», есть ли страница blocked). `third_party_report`: пересказ чужого публичного сообщения (issue, статья), категория выведена из описания.
- `reporter`: кто наблюдал (логин GitHub) или откуда пересказ.
- `source`: ссылка на issue, статью или файл в папке `evidence/` (скриншот только вкладки Response).
- `notes`: что ещё важно: текст окна, версия расширения, оговорки.

Надёжность по убыванию: `devtools_response` > `dialog_observed` > `third_party_report`. Строка с `third_party_report` это не наблюдение участников реестра, а ссылка на чужое сообщение; Anthropic такие сообщения не подтверждала.

## Как проверить свой сайт

### За минуту, по виду окна

Нужен Chrome с расширением Claude. Откройте сайт, в панели Claude напишите: «Открой эту страницу и нажми любую безопасную ссылку в меню. Ничего не вводи и не отправляй». Смотрите на первое окно:

| Что увидели | Категория |
|---|---|
| Страница blocked, сайт не открылся | category1 |
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

**Предупреждение.** Во вкладке Headers рядом виден ваш токен входа в аккаунт Claude. Смотрите только Response. Скриншоты Headers не присылайте никому, в реестр они не принимаются.

Способ в реестре: `devtools_response`.

## Как прислать результат

Два пути:

1. Issue по шаблону «Report a site category»: домен, категория, дата, способ, при желании JSON ответа или скриншот вкладки Response.
2. Pull request: строка в `registry.csv`, скриншот в `evidence/` (имя `домен_категория_ГГГГ-ММ-ДД.webp` или `.png`), затем `python validate.py` и коммит вместе с обновлённым README.

Подробнее в [CONTRIBUTING.md](CONTRIBUTING.md).

## Правила реестра

1. Только собственное наблюдение: ответ сервера или окно разрешения, с датой. Домысел по типу сайта («наверное, банк в category3») не принимается.
2. Массовое автоматическое сканирование через эндпоинт Anthropic не делаем и не просим. Это недокументированный API под личным токеном входа: риск для аккаунта и для условий использования. Записи, полученные скриптом по списку доменов, не принимаются.
3. Категория может меняться. Поэтому дата обязательна, а новое наблюдение того же домена добавляется отдельной строкой, старая не удаляется.
4. Скриншоты вкладки Headers не принимаются: там токен. Только Response.
5. Домен записывается как в ответе сервера (`www.avito.ru`, а не `avito.ru`), поддомены отдельными строками.
6. Чужие публичные сообщения можно вносить как `third_party_report` со ссылкой, но без дорисовки деталей: только то, что написано в источнике.

## Чего реестр не знает

- Критерии, по которым Anthropic относит сайт к категории. Не опубликованы.
- Полный список. Здесь только то, что кто-то проверил.
- Проверяет ли встроенный браузер приложения Claude Desktop категории тем же запросом. По документации Anthropic он сверяется с тем же списком безопасности сайтов, но ответ сервера для него никто из участников не видел.
- Можно ли подать заявку на пересмотр категории. В документации не описано.

## Ссылки

- Справка Anthropic по разрешениям Claude in Chrome: https://support.claude.com/en/articles/12902446-claude-in-chrome-permissions-guide
- Справка «Use Claude in Chrome safely»: https://support.claude.com/en/articles/12902428-use-claude-in-chrome-safely
- Браузер в Claude Desktop для организаций, раздел Site safety check: https://claude.com/docs/third-party/claude-desktop/browser.md
- Claude Code с Chrome: https://code.claude.com/docs/en/chrome.md
- Обращения пользователей в репозитории Claude Code: [99007](https://github.com/anthropics/claude-code/issues/99007), [94880](https://github.com/anthropics/claude-code/issues/94880), [91495](https://github.com/anthropics/claude-code/issues/91495), [93201](https://github.com/anthropics/claude-code/issues/93201)

Реестр не связан с Anthropic. Названия Claude и Anthropic принадлежат их владельцу.
