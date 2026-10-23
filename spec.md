# Техническая спецификация: soc_reports

Документ описывает текущее устройство проекта. При изменении поведения кода обновляйте соответствующий раздел.

## 1. Назначение

Веб-приложение SOC (отдел КЦОКБ). Аналитики регистрируют инциденты (угрозы, выявленные WAF / IPS / EDR / SIEM). Приложение:

- формирует PDF-отчёт по инциденту и отправляет его во внешний сервис cert.gov.kg;
- ведёт список и детальную карточку отчётов;
- формирует ежемесячный отчёт (веб-таблица и экспорт в .docx);
- строит аналитику (графики) и статистическую форму в Excel.

Интерфейс и подписи моделей — на русском языке.

## 2. Стек

| Компонент | Версия / значение |
|---|---|
| Python / Django | Django ~= 5.2.1 |
| БД | PostgreSQL (`psycopg2-binary`) |
| Кэш | Redis (`django.core.cache.backends.redis.RedisCache`, `redis://127.0.0.1:6379`) |
| PDF | reportlab ~= 4.4.0 |
| Word | python-docx ~= 1.1.2 |
| Excel | openpyxl |
| HTTP-клиент | requests |
| API | django-ninja (также установлен djangorestframework, присутствует в `INSTALLED_APPS`) |
| Front-end | Django-шаблоны, Bootstrap-классы, JS в `static/js/analytics/` |

Часовой пояс `UTC`, `USE_TZ = True`, `LANGUAGE_CODE = 'en-us'`.

## 3. Структура проекта

```
project/      настройки, корневой urls.py (+ ninja API), wsgi/asgi
reports/      основное приложение (модели, views, формы)
reports/services/  pdf.py, cert_gov.py, analytics.py, monthly.py, stat_report.py
user/         CustomUser, вход/выход, ninja-роутер создания пользователей
db_logger/    логирование в БД (StatusLog) + опциональная отправка в Telegram
templates/    base.html
static/       css/style.css, js/analytics/*.js
media/        загруженные файлы
logs/         django.log, api.log, reports.log (создаётся автоматически)
```

## 4. Конфигурация

- Переменные окружения читаются из `.env` в корне (python-dotenv, `project/settings.py`). Файл не в git; шаблон — `.env.example`.
- Обязательные: `SECRET_KEY`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`. Остальные: `DEV`, `DEBUG`, `ALLOWED_HOSTS` и `CSRF_TRUSTED_ORIGINS` (через запятую), `DB_HOST`, `DB_PORT`, `SEND_BOT`, `CHAT_ID`, `BOT_ID`.
- БД — только PostgreSQL.
- Интеграция с cert.gov.kg: `CERT_GOV_API_URL`, `CERT_GOV_USERNAME`, `CERT_GOV_PASSWORD` из `.env`; пустой URL отключает отправку. `LOGIN_URL = '/user/login/'`.

## 5. Модель данных

### user.CustomUser
`username` (unique), `username_ru` (unique, nullable), `is_staff`; наследует `AbstractBaseUser` + `PermissionsMixin`. Менеджер: `create_user(password, **fields)`.

### reports.Organization
`name_en` (unique), `name_ru` (unique). Коды в `name_en`, на которые завязан Excel-отчёт: `FIN`, `GTS`, `GNS`, `ADM`.

### reports.Pattern (шаблон атаки)
`name`, `country`, `attack_type`, `description`, `methods`, `detection_tool`, `protocols_ports`, `risk_assessment` (по умолчанию «Низкая»), `potential_impact`, `data_or_payload`, `response_actions`.

### reports.Report (инцидент)
- Связи (все `SET_NULL`): `user`, `organization`, `pattern`.
- Поля: `detection_date`, `country`, `attack_type`, `source_ip`, `destination_ip`, `detection_tool`, `cve`, `host`, `short_description`, `methods`, `protocols_ports`, `potential_impact`, `risk_assessment`, `data_or_payload`, `response_actions`, `created_date` (auto), `pdf_file` (`upload_to='reports/pdfs/'`).
- Справочники:
  - `RISK_LEVELS`: Критическая, Высокая, Средняя, Низкая. Порядок важен: в ежемесячном отчёте для IP выбирается запись с самым высоким уровнем в этом порядке.
  - `DETECTION_TOOLS`: WAF, IPS, EDR, SIEM, Other.

### db_logger.StatusLog
`logger_name`, `level`, `msg`, `trace`, `create_datetime`. При сохранении записей уровня Error (40) и Fatal (50) и `SEND_BOT = True` отправляется сообщение в Telegram (`BOT_ID`, `CHAT_ID`).

## 6. Маршруты

### reports (`app_name='reports'`, подключено в корне `/`)

| URL | View | Назначение |
|---|---|---|
| `/` | `report_create_view` | форма нового отчёта (нужен вход) |
| `/list/` | `ReportListView` | список, пагинация 20, фильтр `start`/`end` (`YYYY-MM-DD`) |
| `/<pk>/` | `ReportDetailView` | карточка отчёта |
| `/download/<pk>/` | `ReportDownloadView` | генерация PDF, отправка в cert.gov.kg, выдача файла |
| `/monthly/` | `MonthlyReportView` | сводка по организации за период; POST правит критичность |
| `/monthly/export/` | `export_monthly_reports` | то же в .docx |
| `/get_departments/` | `get_departments` | JSON `[name_en, name_ru, pk]` |
| `/analytics/` | `analytics_view` | страница аналитики |
| `/analytics-attack-types/` | `get_attack_types_for_chart` | топ-10 типов атак |
| `/analytics-risc-assessments/` | `get_risk_assessments_reports` | распределение по критичности |
| `/analytics-country-attacks/` | `get_countries_attacks` | топ-10 стран |
| `/analytics-ip-counts/` | `get_ip_count` | топ-10 source IP со странами |
| `/analytics-static-reports/` | `get_static_analytic_file` | статистика и Excel (base64 в JSON) |

### Прочее
- `/user/login/`, `/user/logout/` — вход/выход.
- `/api/events/user-create` (POST, django-ninja) — создание пользователя (`username`, `password`, `is_staff`). Аутентификации на эндпоинте нет.
- `/admin/` — админка Django.

## 7. Ключевые потоки

### 7.1 Создание отчёта
1. `ReportsForm` (ModelForm). Поле `pattern` переопределено как `CharField` с `Select`; список шаблонов берётся из БД.
2. В `clean()`: если в `pattern` пришёл числовой id существующего шаблона, берётся он; иначе (произвольный текст) **создаётся новый `Pattern`** с этим именем и полями из отчёта.
3. `detection_date` принимает формат `%Y/%m/%d`.
4. Все шаблоны передаются в страницу как JSON (`model_to_dict`) для автозаполнения полей на клиенте.
5. После сохранения (`report.user = request.user`) редирект на `/?download=<pk>`, что запускает скачивание PDF.

### 7.2 PDF и отправка в cert.gov.kg (`ReportDownloadView`)
1. `_build_report_pdf` собирает A4-таблицу «Поле / Значение» (reportlab). Строка `Host` добавляется для WAF с заполненным `host`, `CVE` — для IPS с `cve`. Текст экранируется (`xml.sax.saxutils.escape`), переносы строк заменяются на `<br/>`.
2. Шрифт: `_report_pdf_font` ищет TTF в путях Linux/Windows (DejaVuSerif, LiberationSerif, times.ttf, arial.ttf) и регистрирует как `TimesNewRoman`; иначе встроенный `Times-Roman` (без кириллицы).
3. Имя файла: `get_valid_filename(f'{pk}_{organization.name_en|report}_{source_ip}.pdf')`.
4. Перед выдачей файла view логинится во внешний API (`/api/token/pair`) и отправляет PDF на `/api/router/report-create` (multipart: `file`, `body` = JSON с `username`, `organization` (ru), `name`; заголовок `Idempotency-Key` = имя файла). Ошибки сети ловятся и пишутся через `print`, пользователю файл выдаётся в любом случае.
5. Текущие адреса в коде — `http://127.0.0.1:8001/...`; боевые (`https://cert.gov.kg/...`) закомментированы.
6. `Report.pdf_file` при скачивании не заполняется (файлы в `reports/pdfs/` попали в репозиторий ранее).

### 7.3 Ежемесячный отчёт
- Фильтры: `org`, `start`, `end`. Выборка по `organization_id` и диапазону `detection_date` (границы суток).
- Для каждого уникального `source_ip`: число запросов, список `destination_ip`, и «представитель» — запись с наивысшим уровнем критичности по порядку `RISK_LEVELS`, при равенстве — самая ранняя.
- POST: поля `manual_priority_<pk>` массово обновляют `risk_assessment` у указанных отчётов, затем редирект с сохранением фильтров.
- Экспорт в .docx: таблица `№ / Destination IP / Source IP / Предупреждение / Критичность`.

### 7.4 Аналитика
- Общий фильтр `get_filtered_qs(start, end)`: без дат берётся текущий день; параметр `department` — id организации.
- Типы атак и страны: топ-10, остальное — «Прочие». Для типов атак значение «Прочие» считается в процентах, а остальные значения — в штуках; для стран — в штуках.
- Ответ содержит `labels`, `data`, `total`, `start`, `end` (для пустой выборки — только пустые `labels`/`data`).

### 7.5 Статистическая Excel-форма
1. `get_static_analytic_file` (параметры `start`, `end` в ISO) считает отчёты, сгруппированные по `user.username`, `organization.name_en`, `risk_assessment`.
2. `create_stat_report` заполняет шаблон `pattern.xlsx` (лист «Лист1»): заголовок в `A2` с периодом, строки пользователей с 7-й; для более чем 4 пользователей вставляются строки с копированием стиля. Итоговая строка — формулы `SUM` по столбцам 4–20.
3. Соответствие столбцов: FIN → D/E, GTS → F/G, GNS → H/I, ADM → N/O (первый — «высокие» = Критическая + Высокая, второй — «низкие» = Средняя + Низкая). Для пользователя без отчётов обнуляются D–I, N, O.
4. Ответ: JSON `{reports, file: {filename: 'report_kcokb.xlsx', content: <base64>, content_type}}`; скачивание собирает front-end.

## 8. Тесты

`reports/tests.py` — `ReportPdfGenerationTests` (`SimpleTestCase`): проверка генерации PDF (спецсимволы, пустые необязательные поля). Запуск: `python manage.py test reports`.

## 9. Известные риски и особенности

- `/api/events/user-create` не требует аутентификации (осознанно не менялось: на него могут опираться внешние вызовы).
- «Прочие» на графике типов атак отдаются в процентах, остальные значения — в штуках; фронтенд (`fillPage.js`) на это рассчитан.
- `Report.pdf_file` при скачивании не заполняется.
- Все веб-страницы и JSON-эндпоинты `reports` требуют входа (`LOGIN_URL = '/user/login/'`). Некорректные `start`/`end` в аналитике дают HTTP 400.
