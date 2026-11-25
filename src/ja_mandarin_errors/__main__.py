"""Command line: python -m ja_mandarin_errors jiā 书 INIT-001 [--lang en] [--json]"""
from __future__ import annotations

import argparse
import json
import sys

from . import KnowledgeBase, __version__


def _print_syllable(r, lang):
    label = r.get("char", "") + (" " if r.get("char") else "") + (r.get("syllable") or r.get("pinyin", "?"))
    print(label)
    if not r["entries"]:
        print("  (no known error in the literature)" if lang == "en" else "  （文献中未见已知偏误）")
    for i in r["entries"]:
        print(f"  {i['code']}  {i['grade']}  {i['note_' + lang]}")


def _print_entry(e, lang):
    name = e["error_name_en"] if lang == "en" else e["error_name_zh"]
    desc = e["description_en"] if lang == "en" else e["description_zh"]
    print(f"{e['error_id']}  [{e['evidence_strength']}]  {name}")
    print(f"  {desc}")
    print(f"  sources: {'; '.join(e['source_refs']) or '—'}")


def main(argv=None):
    ap = argparse.ArgumentParser(prog="python -m ja_mandarin_errors",
                                 description="Look up Mandarin pronunciation errors of native Japanese speakers "
                                             "by pinyin syllable, Chinese text or error code.")
    ap.add_argument("queries", nargs="+", help="e.g. jiā  jia1  nv3  书包  INIT-001")
    ap.add_argument("--lang", choices=["zh", "en"], default="zh")
    ap.add_argument("--json", action="store_true", help="print JSON")
    ap.add_argument("--version", action="version", version=__version__)
    a = ap.parse_args(argv)
    kb = KnowledgeBase()
    results = []
    for q in a.queries:
        try:
            results.append(kb.query(q))
        except (KeyError, ValueError, ImportError) as exc:
            print(f"{q}: {exc}", file=sys.stderr)
            return 1
    if a.json:
        print(json.dumps(results if len(results) > 1 else results[0], ensure_ascii=False, indent=1))
        return 0
    for r in results:
        if isinstance(r, list):
            for x in r:
                _print_syllable(x, a.lang)
        elif "error_id" in r:
            _print_entry(r, a.lang)
        else:
            _print_syllable(r, a.lang)
    return 0


if __name__ == "__main__":
    sys.exit(main())
