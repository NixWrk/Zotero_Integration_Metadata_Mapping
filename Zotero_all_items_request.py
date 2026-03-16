import argparse
import json
import os
import random
import string
from pathlib import Path
from typing import Any, Dict, List, Set

import requests

API_BASE = "https://api.zotero.org"


def _hdr(api_key: str) -> Dict[str, str]:
    return {
        "Zotero-API-Key": api_key,
        "Accept": "application/json",
        "Content-Type": "application/json",
    }


def get_item_types(api_key: str) -> List[str]:
    """RU: Получить список itemType. EN: Fetch all item types."""
    r = requests.get(f"{API_BASE}/itemTypes", headers=_hdr(api_key), timeout=30)
    r.raise_for_status()
    return [x["itemType"] for x in r.json()]


def get_new_item_template(api_key: str, item_type: str) -> Dict[str, Any]:
    """RU: Получить editable-шаблон itemType. EN: Fetch editable itemType template."""
    r = requests.get(
        f"{API_BASE}/items/new",
        params={"itemType": item_type},
        headers=_hdr(api_key),
        timeout=30,
    )
    r.raise_for_status()
    return r.json()


def flatten_keys(obj: Any, prefix: str = "") -> Set[str]:
    """
    RU: Грубая схематизация ключей: возвращает множество путей ключей.
    EN: Rough key schema extraction: returns key-path set.

    Примеры/Examples:
      title
      creators[].firstName
      relations.*
    """
    keys: Set[str] = set()

    if isinstance(obj, dict):
        for k, v in obj.items():
            p = f"{prefix}.{k}" if prefix else k
            keys.add(p)
            keys |= flatten_keys(v, p)
    elif isinstance(obj, list):
        # RU: Для списков обозначаем элемент как [] и продолжаем по первому шаблонному элементу.
        # EN: For lists we mark element as [] and continue from the first template element.
        p = f"{prefix}[]" if prefix else "[]"
        keys.add(p)
        if obj:
            keys |= flatten_keys(obj[0], p)

    return keys


def fill_template_minimally(t: Dict[str, Any], item_type: str) -> Dict[str, Any]:
    """
    RU: Заполняет часть полей заглушками для создания валидного item.
    EN: Fills selected fields with placeholders to create a valid item.
    """
    out = dict(t)
    out["title"] = f"[DUMMY] {item_type} " + "".join(random.choices(string.ascii_letters, k=8))

    # RU: Оставляем одного creator (если поле есть).
    # EN: Keep one creator record (if present).
    if isinstance(out.get("creators"), list) and out["creators"]:
        c0 = dict(out["creators"][0])
        # RU: Zotero допускает (firstName,lastName) или name в зависимости от creatorType.
        # EN: Zotero accepts either (firstName,lastName) or name depending on creatorType.
        if "firstName" in c0 and "lastName" in c0:
            c0["firstName"] = "Test"
            c0["lastName"] = "User"
        elif "name" in c0:
            c0["name"] = "Test User"
        out["creators"] = [c0]

    # RU: Заполняем часть общих полей, если они есть.
    # EN: Fill selected common fields when present.
    for k, v in [
        ("abstractNote", "Dummy abstract"),
        ("url", "https://example.invalid"),
        ("date", "2020-01-01"),
        ("language", "en"),
        ("rights", "Dummy"),
        ("extra", "Dummy"),
    ]:
        if k in out and isinstance(out[k], str):
            out[k] = v

    # RU: tags/collections/relations оставляем как есть: пустые структуры валидны.
    # EN: Keep tags/collections/relations unchanged: empty template structures are valid.
    return out


def create_items(
    api_key: str,
    library_prefix: str,
    items_data: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    RU: POST <userOrGroupPrefix>/items
    EN: POST <userOrGroupPrefix>/items

    RU: Примеры library_prefix.
    EN: library_prefix examples.
      /users/<userID>
      /groups/<groupID>
    """
    url = f"{API_BASE}{library_prefix}/items"
    # RU: Рекомендуется If-Unmodified-Since-Version или Zotero-Write-Token.
    # EN: Recommended headers are If-Unmodified-Since-Version or Zotero-Write-Token.
    # RU: Здесь используем простой write-token.
    # EN: Here we use a simple write-token.
    write_token = "".join(random.choices(string.ascii_lowercase + string.digits, k=32))
    headers = _hdr(api_key)
    headers["Zotero-Write-Token"] = write_token

    r = requests.post(url, headers=headers, data=json.dumps(items_data), timeout=30)
    r.raise_for_status()
    return r.json()


def delete_items(api_key: str, library_prefix: str, item_keys: List[str]) -> None:
    """
    RU: Удаление через DELETE <prefix>/items/<itemKey>.
    EN: Delete items via DELETE <prefix>/items/<itemKey>.

    RU: В API есть bulk delete, здесь простая версия.
    EN: API also supports bulk delete; this implementation is a simple loop.
    """
    for k in item_keys:
        url = f"{API_BASE}{library_prefix}/items/{k}"
        r = requests.delete(url, headers=_hdr(api_key), timeout=30)
        r.raise_for_status()


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--api-key", default=os.environ.get("ZOTERO_API_KEY", ""))
    p.add_argument("--out", default="")
    p.add_argument("--create-dummies", action="store_true")
    p.add_argument("--delete-dummies", action="store_true")
    p.add_argument(
        "--library-prefix",
        default="",
        help=(
            "RU: Например /users/<userID> или /groups/<groupID> (нужно только для create-dummies). "
            "EN: Example /users/<userID> or /groups/<groupID> (required only for create-dummies)."
        ),
    )
    args = p.parse_args()

    out_path = (
        Path(args.out).expanduser()
        if args.out
        else (Path(__file__).resolve().parent / "zotero_template_keys.json")
    )

    print("CWD:", Path.cwd())
    print("Script:", Path(__file__).resolve())
    print("Out file:", out_path)

    if not args.api_key:
        raise SystemExit(
            "RU: Нет API key. Передай --api-key или переменную ZOTERO_API_KEY. "
            "EN: API key is missing. Pass --api-key or set ZOTERO_API_KEY."
        )

    item_types = get_item_types(args.api_key)

    union_flat_keys: Set[str] = set()
    per_type_flat_keys: Dict[str, List[str]] = {}

    templates: Dict[str, Dict[str, Any]] = {}
    for it in item_types:
        t = get_new_item_template(args.api_key, it)
        templates[it] = t
        fk = sorted(flatten_keys(t))
        per_type_flat_keys[it] = fk
        union_flat_keys |= set(fk)

    result = {
        "itemTypes": item_types,
        "unionKeyPaths": sorted(union_flat_keys),
        "perItemTypeKeyPaths": per_type_flat_keys,
        "note": (
            "RU: Ключи получены из /items/new?itemType=... (editable JSON). "
            "EN: Keys are extracted from /items/new?itemType=... (editable JSON)."
        ),
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"Saved: {out_path}", flush=True)
    print(f"Item types: {len(item_types)}")
    print(f"Union key paths: {len(union_flat_keys)}")

    if args.create_dummies:
        if not args.library_prefix:
            raise SystemExit(
                "RU: --library-prefix обязателен для create-dummies (например /users/12345). "
                "EN: --library-prefix is required for create-dummies (e.g. /users/12345)."
            )

        # RU: Создаём по одному dummy item на каждый itemType батчами.
        # EN: Create one dummy item per itemType using batches.
        created_keys: List[str] = []
        batch: List[Dict[str, Any]] = []
        batch_types: List[str] = []

        for it in item_types:
            data = fill_template_minimally(templates[it], it)
            batch.append(data)
            batch_types.append(it)

            # RU: Ограничиваем размер пачки.
            # EN: Limit batch size.
            if len(batch) >= 25:
                resp = create_items(args.api_key, args.library_prefix, batch)
                # RU/EN: success format -> {"0": "<itemKey>", ...}
                created = list(resp.get("success", {}).values())
                created_keys.extend(created)
                print(f"Created {len(created)} dummy items: {batch_types[:3]} ...")
                batch, batch_types = [], []

        if batch:
            resp = create_items(args.api_key, args.library_prefix, batch)
            created = list(resp.get("success", {}).values())
            created_keys.extend(created)
            print(f"Created {len(created)} dummy items (last batch).")

        # RU: При необходимости удаляем только что созданные dummy-записи.
        # EN: Optionally delete the just-created dummy items.
        if args.delete_dummies and created_keys:
            delete_items(args.api_key, args.library_prefix, created_keys)
            print(f"Deleted {len(created_keys)} dummy items.")


if __name__ == "__main__":
    main()
