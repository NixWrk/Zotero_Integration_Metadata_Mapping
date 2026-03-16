import json
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Any, Dict, List, Set


def load_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: str, data: Dict[str, Any]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def compute_union(per_type: Dict[str, List[str]], selected: List[str]) -> List[str]:
    u: Set[str] = set()
    for t in selected:
        u |= set(per_type.get(t, []))
    return sorted(u)


def build_presence_table_md(
    selected_types: List[str],
    per_type_keys: Dict[str, Set[str]],
    union_keys: List[str],
    title: str = "Zotero itemType → keyPath matrix",
) -> str:
    # RU: Markdown-таблица вида keyPath | type1 | type2 | ...
    # EN: Markdown table format: keyPath | type1 | type2 | ...
    # RU: Ограничение: таблица становится очень широкой при большом числе столбцов.
    # EN: Limitation: table becomes very wide with many columns.
    header = ["keyPath"] + selected_types
    sep = ["---"] * len(header)

    lines = []
    lines.append(f"# {title}\n")
    lines.append(f"- Selected itemTypes: {len(selected_types)}")
    lines.append(f"- Union keyPaths: {len(union_keys)}\n")

    lines.append("| " + " | ".join(header) + " |")
    lines.append("| " + " | ".join(sep) + " |")

    for kp in union_keys:
        row = [kp]
        for t in selected_types:
            row.append("✓" if kp in per_type_keys[t] else "")
        lines.append("| " + " | ".join(row) + " |")

    lines.append("")  # RU/EN: trailing newline / перевод строки в конце
    return "\n".join(lines)


class ScrollableFrame(ttk.Frame):
    def __init__(self, container: tk.Widget):
        super().__init__(container)

        canvas = tk.Canvas(self, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # RU: Поддержка колеса мыши (Windows/macOS/Linux).
        # EN: Mouse wheel support (Windows/macOS/Linux).
        def _on_mousewheel(event):
            # RU: Windows — event.delta кратен 120.
            # EN: Windows uses event.delta in multiples of 120.
            # RU: macOS — меньшие дельты; Linux может использовать Button-4/5 (не обработано).
            # EN: macOS uses smaller deltas; Linux may use Button-4/5 (not handled here).
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Select Zotero itemTypes (from JSON)")
        self.geometry("820x620")

        self.json_data: Dict[str, Any] = {}
        self.json_path: str = ""
        self.vars: Dict[str, tk.BooleanVar] = {}

        self._build_ui()

    def _build_ui(self):
        top = ttk.Frame(self)
        top.pack(fill="x", padx=12, pady=10)

        self.path_lbl = ttk.Label(top, text="JSON: (not loaded)")
        self.path_lbl.pack(side="left", fill="x", expand=True)

        load_btn = ttk.Button(top, text="Open JSON…", command=self.on_open)
        load_btn.pack(side="right")

        mid = ttk.Frame(self)
        mid.pack(fill="both", expand=True, padx=12, pady=6)

        left = ttk.Frame(mid)
        left.pack(side="left", fill="both", expand=True)

        self.list_frame = ScrollableFrame(left)
        self.list_frame.pack(fill="both", expand=True)

        right = ttk.Frame(mid)
        right.pack(side="right", fill="y", padx=(10, 0))

        ttk.Label(right, text="Actions").pack(anchor="w")
        ttk.Button(right, text="Select all", command=self.select_all).pack(fill="x", pady=(6, 0))
        ttk.Button(right, text="Clear", command=self.clear_all).pack(fill="x", pady=(6, 0))

        ttk.Separator(right, orient="horizontal").pack(fill="x", pady=12)

        self.stats_lbl = ttk.Label(right, text="Loaded: 0 itemTypes\nSelected: 0")
        self.stats_lbl.pack(anchor="w")

        ttk.Separator(right, orient="horizontal").pack(fill="x", pady=12)

        ttk.Button(right, text="Export reduced JSON + MD…", command=self.on_export).pack(fill="x")

        self.bind("<KeyPress-Escape>", lambda _: self.destroy())

    def on_open(self):
        path = filedialog.askopenfilename(
            title="Open JSON",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if not path:
            return

        try:
            data = load_json(path)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read JSON:\n{e}")
            return

        # RU: Базовая валидация входного JSON.
        # EN: Basic validation for input JSON.
        if "itemTypes" not in data or "perItemTypeKeyPaths" not in data:
            messagebox.showerror(
                "Error",
                "JSON must contain keys: itemTypes, perItemTypeKeyPaths (and optionally unionKeyPaths)."
            )
            return

        self.json_data = data
        self.json_path = path
        self.path_lbl.configure(text=f"JSON: {path}")

        self._render_itemtypes()
        self._update_stats()

    def _render_itemtypes(self):
        # RU: Очистка предыдущего списка.
        # EN: Clear previous list.
        for child in self.list_frame.scrollable_frame.winfo_children():
            child.destroy()

        self.vars.clear()

        item_types: List[str] = list(self.json_data.get("itemTypes", []))
        item_types_sorted = sorted(item_types)

        for t in item_types_sorted:
            v = tk.BooleanVar(value=False)
            self.vars[t] = v
            cb = ttk.Checkbutton(
                self.list_frame.scrollable_frame,
                text=t,
                variable=v,
                command=self._update_stats
            )
            cb.pack(anchor="w", padx=6, pady=2)

    def _update_stats(self):
        loaded = len(self.vars)
        selected = len([t for t, v in self.vars.items() if v.get()])
        self.stats_lbl.configure(text=f"Loaded: {loaded} itemTypes\nSelected: {selected}")

    def select_all(self):
        for v in self.vars.values():
            v.set(True)
        self._update_stats()

    def clear_all(self):
        for v in self.vars.values():
            v.set(False)
        self._update_stats()

    def on_export(self):
        if not self.json_data:
            messagebox.showwarning("Warning", "Load JSON first.")
            return

        selected = [t for t, v in self.vars.items() if v.get()]
        if not selected:
            messagebox.showwarning("Warning", "Select at least one itemType.")
            return

        per_type: Dict[str, List[str]] = self.json_data.get("perItemTypeKeyPaths", {})
        # RU: Нормализуем в set для быстрых membership-проверок.
        # EN: Normalize to sets for fast membership checks.
        per_type_sets: Dict[str, Set[str]] = {t: set(per_type.get(t, [])) for t in selected}
        union_keys = compute_union(per_type, selected)

        # RU: Предупреждение о большом размере экспорта.
        # EN: Warn when export is likely very large.
        if len(selected) > 12 or len(union_keys) > 2000:
            ok = messagebox.askyesno(
                "Large export",
                f"Selected types: {len(selected)}\nUnion keys: {len(union_keys)}\n\n"
                "Markdown table may be very large. Continue?"
            )
            if not ok:
                return

        # RU: Выбор директории для вывода.
        # EN: Choose output directory.
        out_dir = filedialog.askdirectory(title="Select output directory")
        if not out_dir:
            return

        base_name = os.path.splitext(os.path.basename(self.json_path))[0] or "zotero_keys"
        out_json = os.path.join(out_dir, f"{base_name}.selected.json")
        out_md = os.path.join(out_dir, f"{base_name}.selected.md")

        reduced = {
            "itemTypes": selected,
            "unionKeyPaths": union_keys,
            "perItemTypeKeyPaths": {t: sorted(per_type_sets[t]) for t in selected},
            "note": "Reduced from original JSON by selecting itemTypes in GUI; union recomputed."
        }

        try:
            save_json(out_json, reduced)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to write JSON:\n{e}")
            return

        md = build_presence_table_md(
            selected_types=selected,
            per_type_keys=per_type_sets,
            union_keys=union_keys,
            title="Selected Zotero itemTypes: keyPath presence matrix",
        )
        try:
            with open(out_md, "w", encoding="utf-8") as f:
                f.write(md)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to write MD:\n{e}")
            return

        messagebox.showinfo("Done", f"Saved:\n- {out_json}\n- {out_md}")


if __name__ == "__main__":
    App().mainloop()
