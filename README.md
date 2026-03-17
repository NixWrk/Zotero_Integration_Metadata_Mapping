# NIX_Zotero_Obsidian_Metadata_Mapping (RU/EN)

## RU: Зачем этот репозиторий

Прикладное исследование: собрать **максимально полный и проверяемый** список метаданных для работы со связкой Zotero → Obsidian (плагин [Zotero Integration](https://github.com/mgmeyers/obsidian-zotero-integration)).

Главная идея: в интернете и даже в официальной документации мало цельного и воспроизводимого описания всех доступных полей. Здесь сделан набор скетчей, которые позволяют проверять вывод **полуавтоматически и детерминированно**.

## EN: Why this repository exists

A practical research artifact: build a **maximally complete and verifiable** field reference for the Zotero → Obsidian workflow (via the [Zotero Integration](https://github.com/mgmeyers/obsidian-zotero-integration) plugin).

Core motivation: useful information exists online and in docs, but there is little end-to-end, reproducible field mapping for this specific workflow.

---

## RU: Два источника данных — важно понимать разницу

Переменные, доступные в шаблонах плагина, приходят из **двух разных источников**, которые не совпадают:

| Источник | Что даёт | Как получить |
|----------|----------|--------------|
| **Zotero Web API** (`api.zotero.org`) | Схема редактируемых полей по каждому `itemType`: `title`, `creators`, `DOI` и т.д. | Скрипты в этом репо |
| **Плагин Zotero Integration** | Все вышеперечисленное + вычисляемые поля: `citekey`, `attachments[].path`, `annotations[].*`, `bibliography`, `collections[].fullPath` и др. | Анализ `main.js` → [`docs/plugin_template_variables.md`](docs/plugin_template_variables.md) |

**Ключевой вывод:** Web API `/items/new` описывает, *что можно хранить* в Zotero. Плагин же работает через локальный коннектор Zotero-приложения (не Web API) и добавляет поверх собственный слой полей. Для построения шаблона Obsidian нужны **оба** источника.

## EN: Two data sources — important distinction

Template variables available in the plugin come from **two different sources**:

| Source | Provides | How to get |
|--------|----------|------------|
| **Zotero Web API** (`api.zotero.org`) | Editable field schema per `itemType`: `title`, `creators`, `DOI`, etc. | Scripts in this repo |
| **Zotero Integration plugin** | All of the above + computed fields: `citekey`, `attachments[].path`, `annotations[].*`, `bibliography`, `collections[].fullPath`, etc. | Analysis of `main.js` → [`docs/plugin_template_variables.md`](docs/plugin_template_variables.md) |

**Key insight:** The Web API `/items/new` describes *what can be stored* in Zotero. The plugin communicates via the local Zotero app connector (not the Web API) and adds its own field layer on top. Building an Obsidian template requires **both** sources.

---

## RU: Что здесь считается доказанным

- **Доказанные данные:** поля, реально возвращённые Zotero Web API и зафиксированные в JSON-результатах скриптов.
- **Детерминированный режим:** скрипт полного скана не зависит от ручного выбора CAYW.
- **Явные ограничения:** если библиотека недоступна по правам (403), это фиксируется в отчёте, а при `--fail-on-denied` выполнение завершается ошибкой.
- **Переменные плагина:** получены статическим анализом `main.js` (бандл плагина), задокументированы в [`docs/plugin_template_variables.md`](docs/plugin_template_variables.md).

## EN: What is considered proven here

- **Proven data:** fields actually returned by Zotero Web API and written into JSON outputs.
- **Deterministic mode:** full-scan script does not depend on manual CAYW selection.
- **Explicit limitations:** 403-denied libraries are recorded; `--fail-on-denied` exits with error.
- **Plugin variables:** obtained via static analysis of `main.js` (plugin bundle), documented in [`docs/plugin_template_variables.md`](docs/plugin_template_variables.md).

---

## RU: Этапы исследования

1. Получить полный список `itemType` и editable-шаблонов через `/items/new`.
2. Выделить ключи по каждому `itemType` и общий union.
3. Подготовить инструмент фильтрации интересующих `itemType` и табличного сравнения.
4. Добавить детерминированный скан всей доступной библиотеки (user + groups) через Web API.
5. Слить «наблюдённые» поля библиотеки с «гарантированными» полями `/items/new`.
6. Статически проанализировать `main.js` и задокументировать все переменные, которые плагин добавляет в контекст шаблона.

## EN: Research stages

1. Fetch full `itemType` list and editable templates via `/items/new`.
2. Extract key paths per `itemType` and global union.
3. Provide a filter tool for selected `itemType` values and matrix export.
4. Add deterministic full-library scan (user + groups) via Web API.
5. Merge "observed in library" fields with "guaranteed from `/items/new`" fields.
6. Statically analyze `main.js` and document all variables the plugin adds to the template context.

---

## RU: Справочные таблицы

| Документ | Что содержит | Источник |
|----------|-------------|----------|
| [`docs/zotero_api_keypath_matrix.md`](docs/zotero_api_keypath_matrix.md) | Матрица 38 itemTypes × 133 keyPaths из Zotero Web API | `/items/new` → `Zotero_all_items_request.py` |
| [`docs/plugin_template_variables.md`](docs/plugin_template_variables.md) | Полный каталог переменных контекста шаблона плагина Zotero Integration | Статический анализ `main.js` |

## EN: Reference tables

| Document | Contents | Source |
|----------|----------|--------|
| [`docs/zotero_api_keypath_matrix.md`](docs/zotero_api_keypath_matrix.md) | Matrix of 38 itemTypes × 133 keyPaths from Zotero Web API | `/items/new` → `Zotero_all_items_request.py` |
| [`docs/plugin_template_variables.md`](docs/plugin_template_variables.md) | Complete catalog of Zotero Integration plugin template context variables | Static analysis of `main.js` |

---

## RU: Структура репозитория

### Скрипты

- **`Zotero_all_items_request.py`**
  - RU: Получает все `itemType` + `/items/new`-шаблоны, строит `zotero_template_keys.json`.
  - EN: Fetches all `itemType` values + `/items/new` templates, builds `zotero_template_keys.json`.

- **`Zotero_full_library_schema.py`**
  - RU: Детерминированный скан всей доступной библиотеки через Zotero Web API (без CAYW). Строит merged-схему из наблюдённых полей + гарантированных шаблонов.
  - EN: Deterministic scan of all accessible libraries via Zotero Web API (no CAYW). Builds merged schema from observed fields + guaranteed templates.

- **`Json_items_to_md_table.py`**
  - RU: GUI-инструмент. Загружает JSON из скриптов, позволяет отобрать нужные `itemType` и экспортировать урезанный JSON + Markdown-матрицу присутствия полей.
  - EN: GUI tool. Loads JSON from the scripts, lets you select relevant `itemType` values, exports reduced JSON + Markdown presence matrix.

### Документация

- **`docs/plugin_template_variables.md`**
  - RU: Полный каталог переменных контекста шаблона плагина Zotero Integration, полученный статическим анализом `main.js`. Включает: тип, источник, условие появления, описание.
  - EN: Complete catalog of Zotero Integration plugin template context variables, derived from static analysis of `main.js`. Includes: type, source, condition, description.

### Артефакты

- **`main.js`** — RU: Собранный бандл плагина Zotero Integration (референс-артефакт для анализа). EN: Bundled Zotero Integration plugin file (reference artifact for analysis).
- **`Zotero_data_schema.json`** — RU: Большой справочный JSON по типам/полям из источников Zotero. EN: Large reference JSON with Zotero types/fields from Zotero sources.
- **`zotero_template_keys.json`** — RU: Результат запроса `/items/new` по всем `itemType` (компактный справочник). EN: `/items/new` result for all `itemType` values (compact reference).
- **`selected_items/`** — RU: Примеры фильтрации выбранных `itemType` (выход `Json_items_to_md_table.py`). EN: Examples of filtered `itemType` sets (output of `Json_items_to_md_table.py`).

## EN: Repository structure

See the Russian section above — structure is identical, descriptions are bilingual throughout.

---

## RU: Быстрый запуск

### 1) Шаблонные ключи из `/items/new`
```bash
python Zotero_all_items_request.py --api-key <YOUR_KEY>
```

### 2) Детерминированный полный скан библиотеки
```bash
python Zotero_full_library_schema.py --api-key <YOUR_KEY> --out zotero_full_library_schema.json
```

### 3) Строгий режим прав доступа (рекомендуется для CI)
```bash
python Zotero_full_library_schema.py --api-key <YOUR_KEY> --fail-on-denied
```

### 4) GUI: отбор itemType и экспорт таблицы
```bash
python Json_items_to_md_table.py
# Открой zotero_template_keys.json, отметь нужные типы, экспортируй.
```

## EN: Quick start

### 1) Template keys from `/items/new`
```bash
python Zotero_all_items_request.py --api-key <YOUR_KEY>
```

### 2) Deterministic full-library scan
```bash
python Zotero_full_library_schema.py --api-key <YOUR_KEY> --out zotero_full_library_schema.json
```

### 3) Strict access mode (recommended for CI)
```bash
python Zotero_full_library_schema.py --api-key <YOUR_KEY> --fail-on-denied
```

### 4) GUI: select itemTypes and export matrix
```bash
python Json_items_to_md_table.py
# Open zotero_template_keys.json, check desired types, export.
```

---

## RU: Как интерпретировать результат скана

- `meta.deniedLibraries` пустой → скан прошёл по всем доступным библиотекам без отказов.
- `meta.deniedLibraries` не пустой → часть данных недоступна текущему ключу.
- `observedFromLibrary` → поля, фактически найденные в данных вашей библиотеки.
- `templateFromItemsNew` → системно ожидаемые editable-поля по каждому `itemType`.
- `perItemTypeKeyPaths` (root) → итоговый merged union (рекомендуется для построения шаблонов).

## EN: How to interpret scan results

- `meta.deniedLibraries` empty → scan completed all accessible libraries without denials.
- `meta.deniedLibraries` non-empty → part of real data is inaccessible with the current key.
- `observedFromLibrary` → fields actually found in your library data.
- `templateFromItemsNew` → system-level expected editable fields per `itemType`.
- `perItemTypeKeyPaths` (root) → final merged union (recommended for template building).

---

## RU: Ограничения

- Скрипты покрывают только **Zotero Web API**. Поля, добавляемые самим плагином (`citekey`, `attachments[].path`, `annotations[].*`, `bibliography` и др.), Web API не возвращает — они задокументированы отдельно в [`docs/plugin_template_variables.md`](docs/plugin_template_variables.md).
- `observedFromLibrary` зависит от наполнения вашей конкретной библиотеки. Редко используемые поля могут отсутствовать в наблюдённых данных — но они будут присутствовать в `templateFromItemsNew`.
- Для получения `citekey` в шаблонах необходим установленный плагин [Better BibTeX](https://retorque.re/zotero-better-bibtex/).

## EN: Limitations

- Scripts cover only the **Zotero Web API**. Fields added by the plugin itself (`citekey`, `attachments[].path`, `annotations[].*`, `bibliography`, etc.) are not returned by the Web API — they are documented separately in [`docs/plugin_template_variables.md`](docs/plugin_template_variables.md).
- `observedFromLibrary` depends on the contents of your specific library. Rarely-used fields may be absent from observed data — but they will appear in `templateFromItemsNew`.
- `citekey` in templates requires [Better BibTeX](https://retorque.re/zotero-better-bibtex/) to be installed.
