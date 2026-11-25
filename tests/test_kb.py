import io
import subprocess
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ja_mandarin_errors import KnowledgeBase, normalize_pinyin  # noqa: E402
from ja_mandarin_errors.__main__ import main  # noqa: E402

try:
    import pypinyin  # noqa: F401
    HAVE_PYPINYIN = True
except ImportError:
    HAVE_PYPINYIN = False

KB = KnowledgeBase()


class TestPinyin(unittest.TestCase):
    def test_forms(self):
        for s, want in [("jiā", ("jia", 1)), ("jia1", ("jia", 1)), ("JIA1", ("jia", 1)), ("nǚ", ("nv", 3)),
                        ("nü3", ("nv", 3)), ("nu:3", ("nv", 3)), ("lüè", ("lve", 4)), ("de", ("de", None)),
                        ("de5", ("de", 5)), ("de0", ("de", 5)), ("yīng", ("ying", 1))]:
            self.assertEqual(normalize_pinyin(s), want, s)

    def test_bad(self):
        with self.assertRaises(ValueError):
            normalize_pinyin("ji a")


class TestDictionary(unittest.TestCase):
    def test_counts(self):
        self.assertEqual(len(KB.entries()), 31)
        self.assertEqual({g: len(KB.entries(grade=g)) for g in "ABCD"}, {"A": 16, "B": 6, "C": 6, "D": 3})
        self.assertEqual(len(KB.entries(category="tone")), 8)
        self.assertEqual(len(KB.entries(grade="CD")), 9)

    def test_entry(self):
        e = KB.entry("init-001")
        self.assertEqual(e["evidence_strength"], "A")
        self.assertEqual(e["category"], "initial")
        self.assertIn("邓丹 2014", e["source_refs"])
        self.assertTrue(KB.reference("邓丹 2014").startswith("邓丹."))
        with self.assertRaises(KeyError):
            KB.entry("INIT-099")


class TestMapping(unittest.TestCase):
    def test_jia1(self):
        r = KB.syllable("jiā")
        self.assertEqual([(i["code"], i["grade"]) for i in r["entries"]],
                         [("INIT-003", "B"), ("INIT-008", "A"), ("FINA-006", "B"), ("TONE-002", "A")])
        self.assertFalse(r["has_grade_d"])

    def test_examples(self):
        def codes(s):
            return [i["code"] for i in KB.syllable(s)["entries"]]
        self.assertEqual(codes("shū"), ["INIT-001", "INIT-008", "FINA-011", "TONE-002"])
        self.assertEqual(codes("nǚ"), ["INIT-006", "FINA-001", "TONE-001", "TONE-004"])
        self.assertTrue(KB.syllable("nv3")["has_grade_d"])
        self.assertEqual(codes("hao3"), ["INIT-005", "TONE-001", "TONE-004"])

    def test_r_note_kept_whole(self):
        notes = [i["note_zh"] for i in KB.syllable("ran2")["entries"] if i["code"] == "INIT-007"]
        self.assertEqual(len(notes), 1)
        self.assertIn("受英语影响", notes[0])

    def test_toneless_and_neutral(self):
        self.assertNotIn("TONE-002", [i["code"] for i in KB.syllable("jia")["entries"]])
        r = KB.syllable("le5")
        self.assertEqual(r["syllable"], "le5")
        self.assertIn("TONE-005", [i["code"] for i in r["entries"]])
        self.assertEqual(len(KB.neutral_tone_layer), 9)

    def test_interjection_and_unknown(self):
        self.assertTrue(KB.syllable("m2")["interjection"])
        with self.assertRaises(KeyError):
            KB.syllable("xyz1")

    def test_every_note_has_english(self):
        for row in KB.emt_toned["syllables"].values():
            for i in row["entries"]:
                self.assertTrue(i["note_en"])


@unittest.skipUnless(HAVE_PYPINYIN, "pypinyin not installed")
class TestText(unittest.TestCase):
    def test_text(self):
        r = KB.text("你好，书")
        self.assertEqual([x["char"] for x in r], ["你", "好", "书"])
        self.assertEqual(r[2]["syllable"], "shu1")


class TestCLIAndData(unittest.TestCase):
    def test_cli(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            self.assertEqual(main(["jia1", "INIT-001", "--lang", "en"]), 0)
        self.assertIn("INIT-008", buf.getvalue())

    def test_validate_script(self):
        p = subprocess.run([sys.executable, str(ROOT / "scripts" / "validate_data.py")], capture_output=True,
                           text=True)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)


if __name__ == "__main__":
    unittest.main()
