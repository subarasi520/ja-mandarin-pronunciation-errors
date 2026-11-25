"""Query the knowledge base of systematic Mandarin pronunciation errors of native Japanese speakers.

    >>> from ja_mandarin_errors import KnowledgeBase
    >>> kb = KnowledgeBase()
    >>> [e["code"] for e in kb.syllable("jiā")["entries"]]
    ['INIT-003', 'INIT-008', 'FINA-006', 'TONE-002']

Only the standard library is needed. Looking up Chinese characters (``kb.text``) needs the optional
``pypinyin`` package.
"""
from __future__ import annotations

import json
import re
import unicodedata
from functools import cached_property
from pathlib import Path

__version__ = "2.1.2"
__all__ = ["KnowledgeBase", "normalize_pinyin", "__version__"]

_TONE_MARKS = {"̄": 1, "́": 2, "̌": 3, "̀": 4}
_CODE_RE = re.compile(r"^(INIT|FINA|TONE|PROS)-\d{3}$", re.I)
_CJK_RE = re.compile(r"[㐀-鿿豈-﫿]")


def _data_dir() -> Path:
    here = Path(__file__).resolve().parent
    for d in (here / "data", here.parents[1] / "data"):      # installed wheel, then source checkout
        if (d / "ecd.json").exists():
            return d
    raise FileNotFoundError("data files not found next to the package or in the repository")


def normalize_pinyin(s: str) -> tuple[str, int | None]:
    """Turn 'jiā', 'jia1', 'JIA1', 'nǚ', 'nü3', 'nu:3', 'lv4' into ('jia', 1) style.

    Returns (toneless syllable with ü written as v, tone 1-4, 5 for neutral, or None if no tone given).
    """
    s = s.strip().lower().replace("u:", "v").replace("ü", "v")
    tone = None
    m = re.fullmatch(r"([a-zv]+)([0-5])", s)
    if m:
        s, tone = m.group(1), int(m.group(2))
        if tone == 0:
            tone = 5
        return s, tone
    out = []
    for ch in unicodedata.normalize("NFD", s):
        if ch in _TONE_MARKS:
            tone = _TONE_MARKS[ch]
        elif ch == "̈":                                  # combining diaeresis: u + ¨ = ü
            if out and out[-1] == "u":
                out[-1] = "v"
        else:
            out.append(ch)
    base = "".join(out)
    if not re.fullmatch(r"[a-zv]+", base):
        raise ValueError(f"not a pinyin syllable: {s!r}")
    return base, tone


class KnowledgeBase:
    """Error Coding Dictionary (ECD) and Error Mapping Table (EMT), loaded from the bundled JSON files."""

    def __init__(self, data_dir: str | Path | None = None):
        self.data_dir = Path(data_dir) if data_dir else _data_dir()

    def _load(self, name):
        return json.loads((self.data_dir / name).read_text(encoding="utf-8"))

    @cached_property
    def ecd(self) -> dict:
        return self._load("ecd.json")

    @cached_property
    def emt_toned(self) -> dict:
        return self._load("emt_toned.json")

    @cached_property
    def emt_base(self) -> dict:
        return self._load("emt_base.json")

    @cached_property
    def neutral_tone_layer(self) -> list:
        return self._load("neutral_tone_layer.json")["contexts"]

    @cached_property
    def references(self) -> list:
        return self._load("references.json")["references"]

    @cached_property
    def _by_code(self) -> dict:
        return {e["error_id"]: e for e in self.ecd["entries"]}

    @property
    def dataset_id(self) -> str:
        return self.ecd["dataset_id"]

    @property
    def version(self) -> str:
        return self.ecd["version"]

    # ── dictionary ─────────────────────────────────────────────────────
    def entry(self, code: str) -> dict:
        """One ECD entry by its code, e.g. 'INIT-001'."""
        code = code.strip().upper()
        if code not in self._by_code:
            raise KeyError(f"no such entry: {code}")
        return self._by_code[code]

    def entries(self, grade: str | None = None, category: str | None = None,
                modality: str | None = None) -> list[dict]:
        """Filter ECD entries. grade: 'A'-'D' or e.g. 'AB'; category: initial / final / tone / prosody;
        modality: production / perception / production_and_perception."""
        out = self.ecd["entries"]
        if grade:
            out = [e for e in out if e["evidence_strength"] in grade.upper()]
        if category:
            out = [e for e in out if e["category"] == category]
        if modality:
            out = [e for e in out if e["modality"] == modality]
        return list(out)

    def reference(self, short: str) -> str:
        """Full citation for a short form used in source_refs, e.g. '邓丹 2014'."""
        for r in self.references:
            if r["short"] == short:
                return r["full"]
        raise KeyError(short)

    # ── mapping table ──────────────────────────────────────────────────
    def syllable(self, pinyin: str) -> dict:
        """Errors that MAY occur on a syllable. With a tone (1-4) the toned table is used, without a tone
        the toneless (segmental) table; tone 5 returns the segmental entries plus the neutral-tone entry.

        The result has: syllable, initial, final, tone, entries [{code, grade, note_zh, note_en}],
        has_grade_d. Frequencies are NOT given: the table shows possible errors only."""
        base, tone = normalize_pinyin(pinyin)
        if tone in (1, 2, 3, 4):
            key = f"{base}{tone}"
            row = self.emt_toned["syllables"].get(key)
        else:
            key = base
            row = self.emt_base["syllables"].get(key)
        if row is None:
            raise KeyError(f"syllable not in the table: {pinyin!r} -> {key!r}")
        res = {"syllable": f"{base}5" if tone == 5 else key, "tone": tone, **row, "entries": list(row["entries"])}
        if tone == 5:
            e = self.entry("TONE-005")
            res["entries"].append({"code": "TONE-005", "grade": e["evidence_strength"],
                                   "note_zh": "轻声：见轻声层（neutral_tone_layer）",
                                   "note_en": "Neutral tone: see the neutral-tone layer"})
        res["has_grade_d"] = any(i["grade"] == "D" for i in res["entries"])
        return res

    def text(self, text: str) -> list[dict]:
        """Look up every Chinese character of a text (needs `pip install pypinyin`).

        Readings come from pypinyin with its default context handling; tone sandhi is NOT applied,
        so each syllable is looked up in its citation tone. Non-Chinese characters are skipped."""
        try:
            from pypinyin import Style, pinyin
        except ImportError as exc:                              # pragma: no cover
            raise ImportError("kb.text() needs pypinyin: pip install pypinyin") from exc
        chars = [c for c in text if _CJK_RE.match(c)]
        readings = pinyin("".join(chars), style=Style.TONE3, neutral_tone_with_five=True, errors="ignore")
        out = []
        for ch, (py,) in zip(chars, readings):
            try:
                out.append({"char": ch, "pinyin": py, **self.syllable(py)})
            except KeyError:
                out.append({"char": ch, "pinyin": py, "syllable": None, "entries": []})
        return out

    def query(self, s: str):
        """Dispatch: an ECD code, Chinese text, or a pinyin syllable."""
        if _CODE_RE.match(s.strip()):
            return self.entry(s)
        if _CJK_RE.search(s):
            return self.text(s)
        return self.syllable(s)
