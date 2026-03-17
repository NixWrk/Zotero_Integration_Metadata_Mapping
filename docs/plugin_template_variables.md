# Zotero Integration Plugin — Template Context Variables (RU/EN)

## RU: Источник и метод

Этот документ получен **статическим анализом `main.js`** — собранного бандла плагина [Zotero Integration](https://github.com/mgmeyers/obsidian-zotero-integration) (mgmeyers).

Переменные сгруппированы по источнику:
- `zotero` — поле передаётся из Zotero как есть.
- `normalized-zotero` — поле Zotero, но плагин меняет тип/представление (например, строка → `moment`).
- `derived-from-zotero` — новый ключ, детерминированно вычисляемый из полей Zotero.
- `bbt` — поле от Better BibTeX (требует установки плагина BBT).
- `plugin` — поле создаётся логикой плагина, в Zotero отсутствует.

## EN: Source and method

This document was produced via **static analysis of `main.js`** — the compiled bundle of the [Zotero Integration](https://github.com/mgmeyers/obsidian-zotero-integration) plugin (mgmeyers).

Variables are grouped by source:
- `zotero` — field passed from Zotero unchanged.
- `normalized-zotero` — Zotero field, but the plugin changes its type/representation (e.g. string → `moment`).
- `derived-from-zotero` — new key deterministically computed from Zotero fields.
- `bbt` — field from Better BibTeX (requires BBT plugin installed).
- `plugin` — field created by plugin logic, absent in Zotero.

---

## Полная таблица / Full table

| keyPath | type | source | appears_when | notes (RU/EN) |
|---------|------|--------|--------------|---------------|
| `itemType` | string | zotero | always | RU: Тип записи Zotero. EN: Zotero item type. |
| `key` | string | zotero | always | RU: Ключ записи в Zotero (8 символов). EN: Zotero item key (8 chars). |
| `itemKey` | string | zotero | always | RU: Алиас `key` на уровне root item. Используется в шаблоне как `{{itemKey}}`. EN: Alias of `key` at root item level. Used in templates as `{{itemKey}}`. |
| `libraryID` | string \| number | zotero | always | RU: Идентификатор библиотеки Zotero (важно при работе с несколькими библиотеками/группами). EN: Zotero library identifier (important when using multiple libraries or groups). |
| `version` | number | zotero | always | RU: Версия записи (используется для синхронизации). EN: Item version (used for sync). |
| `title` | string | zotero | if set | — |
| `shortTitle` | string | zotero | if set | — |
| `abstractNote` | string | zotero | if set | — |
| `date` | moment \| unknown | normalized-zotero | if `rn(e)` resolved (есть citekey) | RU: Плагин перезаписывает через BBT CSL `issued.date-parts`, строит `moment("YYYY-MM-DD")`. При неуспехе оставляет исходное значение (тип неоднозначен). EN: Plugin overwrites via BBT CSL `issued.date-parts`, builds `moment("YYYY-MM-DD")`. On failure leaves original value (type ambiguous). |
| `dateAdded` | moment | normalized-zotero | if exists | RU: Строка Zotero → `moment`. EN: Zotero string → `moment`. |
| `dateModified` | moment | normalized-zotero | if exists | RU: Строка Zotero → `moment`. EN: Zotero string → `moment`. |
| `accessDate` | moment | normalized-zotero | if exists | RU: Строка Zotero → `moment`. EN: Zotero string → `moment`. |
| `url` | string | zotero | if set | — |
| `DOI` | string | zotero | if set | — |
| `ISBN` | string | zotero | if set | — |
| `ISSN` | string | zotero | if set | — |
| `language` | string | zotero | if set | — |
| `publisher` | string | zotero | if set | — |
| `publicationTitle` | string | zotero | if set | — |
| `pages` | string | zotero | if set | — |
| `volume` | string | zotero | if set | — |
| `issue` | string | zotero | if set | — |
| `extra` | string | zotero | if set | — |
| `rights` | string | zotero | if set | — |
| `libraryCatalog` | string | zotero | if set | — |
| `creators` | array | zotero | always | RU: Массив авторов/редакторов и т.д. EN: Array of authors/editors, etc. |
| `creators[].creatorType` | string | zotero | always | — |
| `creators[].firstName` | string | zotero | if named creator | — |
| `creators[].lastName` | string | zotero | if named creator | — |
| `creators[].name` | string | zotero | if institutional creator | RU: Для организаций (вместо firstName/lastName). EN: For institutional creators (instead of firstName/lastName). |
| `tags` | array | zotero | always | RU: Массив `{tag: string, type?: number}`. EN: Array of `{tag: string, type?: number}`. |
| `tags[].tag` | string | zotero | always | — |
| `relations` | array | normalized-zotero | if original relations exist and non-empty | RU: Нормализуется из объекта Zotero в массив разрешённых объектов (через BBT). EN: Normalized from Zotero object to array of resolved items (via BBT). |
| `relations[].uri` | uri-string | zotero | if relation unresolved | — |
| `relations[].citekey` | string | bbt | if relation resolved to citekey only | — |
| `select` | uri-string | zotero | always | RU: `zotero://select/...` URI от Zotero. EN: `zotero://select/...` URI from Zotero. |
| `uri` | uri-string | zotero | always | — |
| `citekey` | string | bbt | if BBT installed OR already present | RU: Основной ключ цитирования. Нормализует алиасы: `citekey` / `citationKey`. EN: Primary citation key. Normalizes aliases: `citekey` / `citationKey`. |
| `citationKey` | string | bbt | if BBT installed OR already present | RU: Алиас `citekey` для совместимости. EN: Alias of `citekey` for compatibility. |
| `bibliography` | markdown-string | bbt | if BBT installed | RU: Готовое библиографическое описание через BBT JSON-RPC; HTML→Markdown. При ошибке — строка `"Error generating bibliography"`. EN: Formatted bibliography via BBT JSON-RPC; HTML→Markdown. On error — string `"Error generating bibliography"`. |
| `collections` | array | bbt | if BBT installed | RU: Список коллекций через BBT; каждый элемент содержит `key`, `name`, `fullPath`. EN: List of collections via BBT; each element contains `key`, `name`, `fullPath`. |
| `collections[].key` | string | bbt | if collections exist | — |
| `collections[].name` | string | bbt | if collections exist | — |
| `collections[].fullPath` | string | derived-from-zotero | if collections exist | RU: Вычисляется плагином: полный путь коллекции от корня через `/`. EN: Computed by plugin: full collection path from root via `/`. |
| `desktopURI` | uri-string | derived-from-zotero | always | RU: `zotero://select/...` для открытия записи в Zotero Desktop. Строится из `select` либо из `uri`+`itemKey`. EN: `zotero://select/...` for opening the item in Zotero Desktop. Built from `select` or `uri`+`itemKey`. |
| `pdfLink` | markdown-string | derived-from-zotero | if PDF attachment exists | RU: Markdown-ссылка на локальный PDF через `file://...`. EN: Markdown link to local PDF via `file://...`. |
| `pdfZoteroLink` | markdown-string | derived-from-zotero | if PDF attachment exists | RU: Markdown-ссылка на PDF через `zotero://open-pdf/...`. EN: Markdown link to PDF via `zotero://open-pdf/...`. |
| `markdownNotes` | markdown-string | derived-from-zotero | if notes exist | RU: Все `notes[].note` (Markdown), склеенные через пустую строку. EN: All `notes[].note` (Markdown), joined by blank lines. |
| `allTags` | string | derived-from-zotero | if tags exist | RU: `"tag1, tag2, ..."`. EN: `"tag1, tag2, ..."`. |
| `hashTags` | string | derived-from-zotero | if tags exist | RU: `"#tag-one, #tag-two"`. Пробелы → дефисы. EN: `"#tag-one, #tag-two"`. Spaces → dashes. |
| `*(creatorType)s` | markdown-string | derived-from-zotero | if creators of given type exist | RU: Динамические ключи вида `authors`, `editors`, … — по одному на каждый `creatorType`. EN: Dynamic keys like `authors`, `editors`, … — one per `creatorType` present. |
| `formattedAnnotations` | markdown-string | derived-from-zotero | if annotations exist | RU: Все аннотации в Markdown (фильтр `lastExportDate = moment(0)` — «все»). EN: All annotations in Markdown (filter `lastExportDate = moment(0)` — "all"). |
| `formattedAnnotationsNew` | markdown-string | derived-from-zotero | if new annotations exist | RU: Только аннотации новее `lastExportDate`. EN: Only annotations newer than `lastExportDate`. |
| `importDate` | moment | plugin | always | RU: Момент текущего запуска импорта. EN: Moment of the current import run. |
| `exportDate` | moment | plugin | always | RU: Момент текущего экспорта/рендера. EN: Moment of current export/render. |
| `lastImportDate` | moment | plugin | always | RU: Дата предыдущего импорта из маркера файла. `moment(0)` при первом импорте. EN: Date of previous import from file marker. `moment(0)` on first import. |
| `lastExportDate` | moment | plugin | always | RU: Нижняя граница для фильтрации аннотаций (`formattedAnnotationsNew`). EN: Lower bound for annotation filtering (`formattedAnnotationsNew`). |
| `isFirstImport` | boolean | plugin | always | RU: `true`, если `lastImportDate === moment(0)`. EN: `true` if `lastImportDate === moment(0)`. |
| `_retained` | object | plugin | if persist blocks exist in file | RU: Контейнер сохранённых вручную блоков: `_retained[name] = text`. Парсятся из `%% begin <name> %% ... %% end <name> %%`. EN: Container for manually-retained blocks: `_retained[name] = text`. Parsed from `%% begin <name> %% ... %% end <name> %%`. |
| `_retained.*` | string | plugin | if corresponding persist block exists | RU: Динамический ключ = имя блока `persist`. EN: Dynamic key = name of `persist` block. |

---

## Вложенные объекты / Nested objects

### `attachments[]`

| keyPath | type | source | appears_when | notes (RU/EN) |
|---------|------|--------|--------------|---------------|
| `attachments[].key` | string | zotero | always | — |
| `attachments[].itemKey` | string | derived-from-zotero | if `uri` exists | RU: Последний сегмент `uri`. EN: Last segment of `uri`. |
| `attachments[].title` | string | zotero | if set | RU: Название вложения (обычно имя файла без расширения). EN: Attachment title (usually filename without extension). |
| `attachments[].path` | string | zotero | if local file | RU: Абсолютный путь к файлу в локальной ФС. EN: Absolute path to the file in local filesystem. |
| `attachments[].uri` | uri-string | zotero | always | — |
| `attachments[].desktopURI` | uri-string | derived-from-zotero | if `uri` exists | RU: `zotero://select/...` для вложения. EN: `zotero://select/...` for the attachment. |
| `attachments[].pdfURI` | uri-string | derived-from-zotero | if path ends with `.pdf` | RU: `zotero://open-pdf/...`. EN: `zotero://open-pdf/...`. |
| `attachments[].dateAdded` | moment | normalized-zotero | if exists | — |
| `attachments[].dateModified` | moment | normalized-zotero | if exists | — |

### `annotations[]`

RU: Аннотации первого PDF-вложения. Массив всегда присутствует (может быть пустым).
EN: Annotations from the first PDF attachment. Array is always present (may be empty).

| keyPath | type | source | appears_when | notes (RU/EN) |
|---------|------|--------|--------------|---------------|
| `annotations[].id` | string | zotero | always | RU: Ключ аннотации (`e.key`). EN: Annotation key (`e.key`). |
| `annotations[].type` | string | zotero | always | RU: Тип аннотации (`annotationType`): highlight, underline, note, image и т.д. EN: Annotation type (`annotationType`): highlight, underline, note, image, etc. |
| `annotations[].source` | string | plugin | always | RU: `"zotero"` для аннотаций Zotero, `"pdf"` для аннотаций PDF-utility. EN: `"zotero"` for Zotero annotations, `"pdf"` for PDF-utility annotations. |
| `annotations[].date` | moment | normalized-zotero | always | RU: `moment(e.dateModified)`. EN: `moment(e.dateModified)`. |
| `annotations[].attachment` | object | zotero | always | RU: Ссылка на объект attachment (используется для построения ссылок). EN: Reference to the attachment object (used for building links). |
| `annotations[].desktopURI` | uri-string | derived-from-zotero | always | RU: `zotero://open-pdf/...` с параметрами страницы/аннотации. EN: `zotero://open-pdf/...` with page/annotation params. |
| `annotations[].page` | number | derived-from-zotero | always | RU: `pageIndex + 1`. EN: `pageIndex + 1`. |
| `annotations[].pageLabel` | string \| number | derived-from-zotero | always | RU: Метка страницы (может быть строкой при нестандартной нумерации PDF). EN: Page label (may be a string for non-standard PDF pagination). |
| `annotations[].annotatedText` | string | zotero | if annotation has text | RU: Выделенный текст (`annotationText`). EN: Highlighted text (`annotationText`). |
| `annotations[].comment` | string | zotero | if annotation has comment | RU: Комментарий пользователя (`annotationComment`). Может быть конкатенирован при `shouldConcat`. EN: User comment (`annotationComment`). May be concatenated when `shouldConcat` is active. |
| `annotations[].color` | string | zotero | if set | RU: Hex-цвет аннотации (`annotationColor`). EN: Hex color of the annotation (`annotationColor`). |
| `annotations[].colorCategory` | string | derived-from-zotero | if `color` exists | RU: Категория цвета (Yellow/Red/Green/Blue/Purple/Orange/Grey), вычисляется функцией `Px(color)`. EN: Color category (Yellow/Red/Green/Blue/Purple/Orange/Grey), computed by `Px(color)`. |
| `annotations[].x` | number | derived-from-zotero | if rects available | RU: X-координата прямоугольника аннотации. EN: X coordinate of annotation rect. |
| `annotations[].y` | number | derived-from-zotero | if rects available | RU: Y-координата прямоугольника аннотации. EN: Y coordinate of annotation rect. |
| `annotations[].imagePath` | string | derived-from-zotero | if image annotation | RU: Путь к файлу изображения (скрин аннотации). EN: Path to image file (annotation screenshot). |
| `annotations[].imageBaseName` | string | derived-from-zotero | if `imagePath` exists | RU: Базовое имя файла изображения. EN: Base filename of the image. |
| `annotations[].imageExtension` | string | derived-from-zotero | if `imagePath` exists | RU: Расширение без точки (например `png`). EN: Extension without dot (e.g. `png`). |
| `annotations[].imageRelativePath` | string | derived-from-zotero | if `imagePath` exists | RU: Относительный путь для вставки `![[...]]` в Obsidian. EN: Relative path for `![[...]]` embed in Obsidian. |
| `annotations[].ocrText` | string | derived-from-zotero | if PDF-utility OCR available | RU: OCR-текст изображения аннотации (только при использовании PDF-utility с поддержкой OCR). EN: OCR text of image annotation (only when using PDF-utility with OCR support). |
| `annotations[].tags` | array | zotero | if annotation has tags | RU: Теги аннотации. EN: Annotation tags. |
| `annotations[].allTags` | string | derived-from-zotero | if annotation tags exist | RU: `"tag1, tag2, ..."` на уровне аннотации. EN: `"tag1, tag2, ..."` at annotation level. |
| `annotations[].hashTags` | string | derived-from-zotero | if annotation tags exist | RU: `"#tag-one, ..."` на уровне аннотации. EN: `"#tag-one, ..."` at annotation level. |

### `notes[]`

| keyPath | type | source | appears_when | notes (RU/EN) |
|---------|------|--------|--------------|---------------|
| `notes[].note` | markdown-string | normalized-zotero | if note has content | RU: HTML заметки Zotero → Markdown (через `htmlToMarkdown`). EN: Zotero note HTML → Markdown (via `htmlToMarkdown`). |
| `notes[].desktopURI` | uri-string | derived-from-zotero | if `uri` exists | RU: `zotero://select/...` для перехода к заметке. EN: `zotero://select/...` to navigate to the note. |
| `notes[].dateAdded` | moment | normalized-zotero | if exists | — |
| `notes[].dateModified` | moment | normalized-zotero | if exists | — |
| `notes[].relations` | array | normalized-zotero | if note has relations | RU: Аналогично root `relations`. EN: Same as root `relations`. |

---

## RU: Примечания

- **`moment`-объекты** форматируются в шаблоне через фильтр `format`, например: `{{ dateAdded | format("YYYY-MM-DD HH:mm") }}`.
- **`citekey` / `citationKey`** требуют установленного [Better BibTeX](https://retorque.re/zotero-better-bibtex/). Без BBT эти поля могут быть пустыми.
- **`collections[].fullPath`** строится плагином путём подъёма по `parentCollection` — это вычисляемое поле, которого нет в Zotero Web API.
- **`_retained`** реализован расширением `PersistExtension` плагина; блоки обрамляются в шаблоне через `{% persist "name" %} ... {% endpersist %}`.
- **`ocrText`** появляется только при использовании PDF-utility-режима с поддержкой OCR; в стандартном режиме Zotero аннотаций это поле отсутствует.

## EN: Notes

- **`moment` objects** are formatted in templates via the `format` filter, e.g.: `{{ dateAdded | format("YYYY-MM-DD HH:mm") }}`.
- **`citekey` / `citationKey`** require [Better BibTeX](https://retorque.re/zotero-better-bibtex/) to be installed. Without BBT these fields may be empty.
- **`collections[].fullPath`** is built by the plugin by traversing `parentCollection` — a computed field absent from the Zotero Web API.
- **`_retained`** is implemented by the plugin's `PersistExtension`; blocks are wrapped in templates via `{% persist "name" %} ... {% endpersist %}`.
- **`ocrText`** appears only when using PDF-utility mode with OCR support; in standard Zotero annotation mode this field is absent.
