# NIX_Zotero_Obsidian_Metadata_Mapping (RU/EN)

## RU: Зачем этот репозиторий
Этот репозиторий — результат прикладного исследования: собрать **максимально полный и проверяемый** список метаданных, которые можно использовать при импорте литературы из Zotero в Obsidian (в контексте шаблонов для плагина Zotero Integration).

Главная идея: в интернете и даже в официальной документации по этой связке есть полезные фрагменты, но мало цельного и воспроизводимого описания полей. Поэтому здесь сделан набор скетчей, которые позволяют проверять вывод **полуавтоматически и детерминированно**.

Это не «идеальный конечный шаблон», а рабочий инженерный шаг к нему.

## EN: Why this repository exists
This repository is a practical research artifact: to build a **maximally complete and verifiable** list of metadata available when importing literature from Zotero into Obsidian (for Zotero Integration templates).

The core motivation: useful information exists online and in docs, but there is still little end-to-end, reproducible field mapping for this specific workflow. This repo provides sketches to validate output **semi-automatically and deterministically**.

This is not the final “perfect template”, but a solid engineering step toward it.

---

## RU: Что здесь считается доказанным
- Доказанные данные: поля, реально возвращённые Zotero Web API и зафиксированные в JSON-результатах скриптов.
- Детерминированный режим: скрипт полного скана не зависит от ручного выбора CAYW.
- Явные ограничения: если библиотека недоступна по правам (403), это фиксируется в отчёте, а при `--fail-on-denied` выполнение завершается ошибкой.

## EN: What is considered proven here
- Proven data: fields actually returned by Zotero Web API and written into JSON outputs.
- Deterministic mode: full-scan script does not depend on manual CAYW selection.
- Explicit limitations: if a library is inaccessible (403), this is recorded; with `--fail-on-denied` the script exits with an error.

---

## RU: Этапы исследования
1. Получить полный список `itemType` и editable-шаблонов через `/items/new`.
2. Выделить ключи по каждому `itemType` и общий union.
3. Подготовить инструмент фильтрации интересующих `itemType` и табличного сравнения.
4. Добавить детерминированный скан всей доступной библиотеки (user + groups) через Web API.
5. Слить «наблюдённые» поля библиотеки с «гарантированными» полями `/items/new`.

## EN: Research stages
1. Fetch full `itemType` list and editable templates via `/items/new`.
2. Extract key paths per `itemType` and global union.
3. Provide a filter tool for selected `itemType` values and matrix export.
4. Add deterministic full-library scan (user + groups) via Web API.
5. Merge “observed in library” fields with “guaranteed from `/items/new`” fields.

---

## RU: Назначение каждого скетча
- `Zotero_all_items_request.py`
  - RU: Получает `itemType` + `/items/new` и строит `zotero_template_keys.json`.
  - EN: Fetches `itemType` + `/items/new` and builds `zotero_template_keys.json`.

- `Json_items_to_md_table.py`
  - RU: GUI-инструмент для выбора интересующих `itemType`, экспорта урезанного JSON и MD-матрицы присутствия полей.
  - EN: GUI tool to select relevant `itemType` values and export reduced JSON + Markdown presence matrix.

- `Zotero_full_library_schema.py`
  - RU: Детерминированный скан всей доступной библиотеки через Zotero Web API (без CAYW).
  - EN: Deterministic scan of all accessible libraries via Zotero Web API (no CAYW).
  - RU: Выход включает:
  - EN: Output includes:
    - `observedFromLibrary` — RU: реально наблюдённые поля в вашей библиотеке / EN: fields actually observed in your library.
    - `templateFromItemsNew` — RU: гарантированные editable-поля по всем `itemType` / EN: guaranteed editable fields for all `itemType` values.
    - `perItemTypeKeyPaths` и `unionKeyPaths` — RU: объединённая схема / EN: merged schema.

---

## RU: Файлы репозитория
- `main.js` — RU: собранный файл плагина Zotero Integration (референс артефакт). EN: bundled Zotero Integration plugin file (reference artifact).
- `Zotero_data_schema.json` — RU: большой справочный JSON по типам/полям из Zotero-источников. EN: large reference JSON with Zotero types/fields.
- `zotero_template_keys.json` — RU: результат запроса `/items/new` (компактный практический справочник). EN: `/items/new` result (compact practical reference).
- `selected_items/` — RU: примеры фильтрации выбранных `itemType`. EN: examples of filtered selected `itemType` sets.

---

## RU: Быстрый запуск
### 1) Шаблонные ключи `/items/new`
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

---

## RU: Как интерпретировать результат
- Если `meta.deniedLibraries` пустой — RU: скан прошёл по всем доступным библиотекам без отказов. EN: scan completed without denied libraries.
- Если `meta.deniedLibraries` не пустой — RU: часть фактических данных недоступна текущему ключу. EN: part of real data is inaccessible with the current key.
- `observedFromLibrary` — RU: фактически найденные поля в данных. EN: fields actually found in data.
- `templateFromItemsNew` — RU: системно ожидаемые editable-поля. EN: system-level expected editable fields.
- Итоговая merged-схема — RU: лучший практический компромисс между «гарантированным» и «наблюдённым». EN: best practical merge of guaranteed and observed fields.

---

## RU: Почему это шаг к идеальному шаблону Zotero Integration
Идеальный шаблон требует:
- полного поля-списка,
- понимания, какие поля реально заполняются в вашей библиотеке,
- регулярной проверки на изменения.

Этот репозиторий закрывает эти три пункта: здесь есть источник, сравнение и повторяемый способ проверки.

## EN: Why this is a step toward an ideal Zotero Integration template
An ideal template needs:
- a complete field list,
- understanding of what is actually populated in your library,
- repeatable checks for changes over time.

This repository addresses all three: source mapping, comparison, and repeatable verification.
