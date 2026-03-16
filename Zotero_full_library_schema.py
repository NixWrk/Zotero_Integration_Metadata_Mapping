"""
RU: Р”РµС‚РµСЂРјРёРЅРёСЂРѕРІР°РЅРЅС‹Р№ СЃР±РѕСЂ СЃС…РµРјС‹ РјРµС‚Р°РґР°РЅРЅС‹С… Zotero Р±РµР· СЂСѓС‡РЅРѕРіРѕ РІС‹Р±РѕСЂР° РІ UI.
EN: Deterministic Zotero metadata schema collection without manual UI selection.
"""

import argparse
import json
import os
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Set

import requests


API_BASE = "https://api.zotero.org"


def _headers(api_key: str) -> Dict[str, str]:
    return {
        "Zotero-API-Key": api_key,
        "Accept": "application/json",
        "Content-Type": "application/json",
    }


def _get_json(url: str, api_key: str, params: Dict[str, Any], timeout: int) -> Any:
    try:
        r = requests.get(url, headers=_headers(api_key), params=params, timeout=timeout)
        r.raise_for_status()
        return r.json()
    except requests.HTTPError as exc:
        status = exc.response.status_code if exc.response is not None else None
        if status == 403:
            raise PermissionError(f"Forbidden: {url}") from exc
        raise RuntimeError(f"HTTP GET failed: {url} :: {exc}") from exc
    except requests.RequestException as exc:
        raise RuntimeError(f"HTTP GET failed: {url} :: {exc}") from exc


def flatten_keys(obj: Any, prefix: str = "") -> Set[str]:
    keys: Set[str] = set()

    if isinstance(obj, dict):
        for k, v in obj.items():
            p = f"{prefix}.{k}" if prefix else k
            keys.add(p)
            keys |= flatten_keys(v, p)
    elif isinstance(obj, list):
        p = f"{prefix}[]" if prefix else "[]"
        keys.add(p)
        for x in obj:
            keys |= flatten_keys(x, p)

    return keys


def get_key_profile(api_key: str, timeout: int) -> Dict[str, Any]:
    try:
        data = _get_json(f"{API_BASE}/keys/current", api_key, {}, timeout)
    except Exception as exc:
        raise SystemExit(str(exc)) from exc
    if not isinstance(data, dict):
        raise SystemExit("Unexpected response from /keys/current.")
    return data


def get_user_id(profile: Dict[str, Any]) -> int:
    user_id = profile.get("userID")
    if isinstance(user_id, int):
        return user_id
    if isinstance(user_id, str) and user_id.isdigit():
        return int(user_id)
    raise SystemExit("Cannot resolve userID from /keys/current response.")


def list_group_ids(api_key: str, user_id: int, timeout: int) -> List[int]:
    try:
        data = _get_json(f"{API_BASE}/users/{user_id}/groups", api_key, {}, timeout)
    except PermissionError:
        return []
    except RuntimeError:
        return []
    if not isinstance(data, list):
        return []

    out: List[int] = []
    for g in data:
        if not isinstance(g, dict):
            continue
        if isinstance(g.get("id"), int):
            out.append(g["id"])
            continue
        if isinstance(g.get("id"), str) and g["id"].isdigit():
            out.append(int(g["id"]))
            continue
        d = g.get("data")
        if isinstance(d, dict):
            if isinstance(d.get("id"), int):
                out.append(d["id"])
            elif isinstance(d.get("id"), str) and d["id"].isdigit():
                out.append(int(d["id"]))
    return sorted(set(out))


def get_item_types(api_key: str, timeout: int) -> List[str]:
    try:
        data = _get_json(f"{API_BASE}/itemTypes", api_key, {}, timeout)
    except Exception as exc:
        raise SystemExit(str(exc)) from exc
    if not isinstance(data, list):
        raise SystemExit("Unexpected response from /itemTypes.")
    out: List[str] = []
    for x in data:
        if isinstance(x, dict) and isinstance(x.get("itemType"), str):
            out.append(x["itemType"])
    return sorted(set(out))


def get_new_item_template(api_key: str, item_type: str, timeout: int) -> Dict[str, Any]:
    try:
        data = _get_json(
            f"{API_BASE}/items/new",
            api_key,
            {"itemType": item_type},
            timeout,
        )
    except Exception as exc:
        raise SystemExit(str(exc)) from exc
    if not isinstance(data, dict):
        raise SystemExit(f"Unexpected template for itemType={item_type}.")
    return data


def fetch_all_items(
    api_key: str,
    library_prefix: str,
    timeout: int,
    include_trashed: bool,
    page_limit: int,
) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    start = 0
    while True:
        # RU: РџРѕСЃС‚СЂР°РЅРёС‡РЅС‹Р№ РїСЂРѕС…РѕРґ РїРѕ Р±РёР±Р»РёРѕС‚РµРєРµ.
        # EN: Paginated library scan.
        params: Dict[str, Any] = {"start": start, "limit": page_limit}
        if include_trashed:
            params["includeTrashed"] = 1

        batch = _get_json(f"{API_BASE}{library_prefix}/items", api_key, params, timeout)
        if not isinstance(batch, list):
            raise SystemExit(f"Unexpected /items response for {library_prefix}.")
        if not batch:
            break

        out.extend(x for x in batch if isinstance(x, dict))
        if len(batch) < page_limit:
            break
        start += len(batch)

    return out


def build_observed_per_type(items: Iterable[Dict[str, Any]]) -> Dict[str, Set[str]]:
    per_type: Dict[str, Set[str]] = defaultdict(set)
    for item in items:
        data = item.get("data")
        if not isinstance(data, dict):
            continue
        item_type = str(data.get("itemType") or "unknown")
        per_type[item_type] |= flatten_keys(data)
    return per_type


def build_template_per_type(api_key: str, item_types: List[str], timeout: int) -> Dict[str, Set[str]]:
    out: Dict[str, Set[str]] = {}
    for item_type in item_types:
        tmpl = get_new_item_template(api_key, item_type, timeout)
        out[item_type] = flatten_keys(tmpl)
    return out


def count_items_by_type(items: Iterable[Dict[str, Any]]) -> Dict[str, int]:
    counts: Dict[str, int] = defaultdict(int)
    for item in items:
        data = item.get("data")
        if not isinstance(data, dict):
            continue
        item_type = str(data.get("itemType") or "unknown")
        counts[item_type] += 1
    return dict(sorted(counts.items()))


def merge_per_type(
    observed: Dict[str, Set[str]],
    template: Dict[str, Set[str]],
) -> Dict[str, Set[str]]:
    merged: Dict[str, Set[str]] = defaultdict(set)
    for t, keys in template.items():
        merged[t] |= keys
    for t, keys in observed.items():
        merged[t] |= keys
    return dict(sorted(merged.items()))


def collect_union(per_type: Dict[str, Set[str]]) -> List[str]:
    u: Set[str] = set()
    for keys in per_type.values():
        u |= keys
    return sorted(u)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "RU: Р”РµС‚РµСЂРјРёРЅРёСЂРѕРІР°РЅРЅРѕ СЃС‚СЂРѕРёС‚ СЃС…РµРјСѓ Zotero РёР· РїРѕР»РЅРѕРіРѕ СЃРєР°РЅР° Р±РёР±Р»РёРѕС‚РµРєРё + /items/new "
            "(Р±РµР· СЂСѓС‡РЅРѕРіРѕ РІС‹Р±РѕСЂР° CAYW). "
            "EN: Builds deterministic Zotero schema from full library scan + /items/new templates "
            "(no manual CAYW selection)."
        )
    )
    parser.add_argument("--api-key", default=os.environ.get("ZOTERO_API_KEY", ""))
    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument("--page-limit", type=int, default=100)
    parser.add_argument("--skip-groups", action="store_true")
    parser.add_argument("--exclude-trashed", action="store_true")
    parser.add_argument(
        "--fail-on-denied",
        action="store_true",
        help=(
            "RU: Р—Р°РІРµСЂС€Р°С‚СЊ РІС‹РїРѕР»РЅРµРЅРёРµ СЃ РѕС€РёР±РєРѕР№, РµСЃР»Рё С…РѕС‚СЏ Р±С‹ РѕРґРЅР° Р±РёР±Р»РёРѕС‚РµРєР° РЅРµРґРѕСЃС‚СѓРїРЅР° (403). "
            "EN: Exit with error if at least one library is inaccessible (403)."
        ),
    )
    parser.add_argument("--out", default="")
    args = parser.parse_args()

    if not args.api_key:
        raise SystemExit(
            "RU: РџРµСЂРµРґР°Р№ --api-key РёР»Рё СѓСЃС‚Р°РЅРѕРІРё ZOTERO_API_KEY. "
            "EN: Provide --api-key or set ZOTERO_API_KEY."
        )

    out_path = (
        Path(args.out).expanduser()
        if args.out
        else (Path(__file__).resolve().parent / "zotero_full_library_schema.json")
    )

    profile = get_key_profile(args.api_key, args.timeout)
    user_id = get_user_id(profile)

    prefixes = [f"/users/{user_id}"]
    if not args.skip_groups:
        group_ids = list_group_ids(args.api_key, user_id, args.timeout)
        prefixes.extend(f"/groups/{gid}" for gid in group_ids)
    else:
        group_ids = []

    all_items: List[Dict[str, Any]] = []
    items_by_library: Dict[str, int] = {}
    denied_libraries: List[str] = []
    for p in prefixes:
        try:
            items = fetch_all_items(
                api_key=args.api_key,
                library_prefix=p,
                timeout=args.timeout,
                include_trashed=not args.exclude_trashed,
                page_limit=args.page_limit,
            )
            all_items.extend(items)
            items_by_library[p] = len(items)
        except PermissionError:
            denied_libraries.append(p)
            items_by_library[p] = 0
        except RuntimeError as exc:
            raise SystemExit(str(exc)) from exc

    if args.fail_on_denied and denied_libraries:
        denied = ", ".join(denied_libraries)
        raise SystemExit(
            "RU: РћР±РЅР°СЂСѓР¶РµРЅС‹ РЅРµРґРѕСЃС‚СѓРїРЅС‹Рµ Р±РёР±Р»РёРѕС‚РµРєРё (403): "
            f"{denied}. "
            "EN: Inaccessible libraries detected (403): "
            f"{denied}."
        )

    item_types = get_item_types(args.api_key, args.timeout)
    template_per = build_template_per_type(args.api_key, item_types, args.timeout)
    observed_per = build_observed_per_type(all_items)
    merged_per = merge_per_type(observed_per, template_per)

    result = {
        "meta": {
            "generatedAt": datetime.now(timezone.utc).isoformat(),
            "scanMode": "full-library-web-api",
            "userID": user_id,
            "groupIDsScanned": group_ids,
            "librariesScanned": prefixes,
            "itemsByLibrary": items_by_library,
            "deniedLibraries": denied_libraries,
            "totalItemsScanned": len(all_items),
            "excludeTrashed": bool(args.exclude_trashed),
            "pageLimit": args.page_limit,
        },
        "itemTypes": sorted(merged_per.keys()),
        "unionKeyPaths": collect_union(merged_per),
        "perItemTypeKeyPaths": {k: sorted(v) for k, v in merged_per.items()},
        "observedFromLibrary": {
            "itemTypes": sorted(observed_per.keys()),
            "unionKeyPaths": collect_union(observed_per),
            "perItemTypeKeyPaths": {k: sorted(v) for k, v in sorted(observed_per.items())},
            "itemTypeCounts": count_items_by_type(all_items),
        },
        "templateFromItemsNew": {
            "itemTypes": sorted(template_per.keys()),
            "unionKeyPaths": collect_union(template_per),
            "perItemTypeKeyPaths": {k: sorted(v) for k, v in sorted(template_per.items())},
        },
        "note": (
            "RU: РС‚РѕРіРѕРІР°СЏ СЃС…РµРјР° = РЅР°Р±Р»СЋРґР°РµРјС‹Рµ РєР»СЋС‡Рё РёР· РІСЃРµС… РґРѕСЃС‚СѓРїРЅС‹С… Р±РёР±Р»РёРѕС‚РµРє + РіР°СЂР°РЅС‚РёСЂРѕРІР°РЅРЅС‹Рµ "
            "СЂРµРґР°РєС‚РёСЂСѓРµРјС‹Рµ РєР»СЋС‡Рё РёР· /items/new РґР»СЏ РєР°Р¶РґРѕРіРѕ itemType. "
            "EN: Merged schema = observed keys from all accessible libraries + guaranteed editable "
            "keys from /items/new for each itemType."
        ),
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"Saved: {out_path}")
    print(f"Libraries scanned: {len(prefixes)}")
    print(f"Total items scanned: {len(all_items)}")
    print(f"Merged itemTypes: {len(result['itemTypes'])}")
    print(f"Merged union key paths: {len(result['unionKeyPaths'])}")
    print(f"Observed itemTypes: {len(result['observedFromLibrary']['itemTypes'])}")


if __name__ == "__main__":
    main()
