# Mandarin pronunciation errors of native Japanese speakers: a knowledge base

[中文](README.md) · [日本語](README.ja.md) · Version 2.1.1 · **Non-commercial license: research and non-profit teaching** ([LICENSE](LICENSE))

A structured, evidence-graded summary of what published studies say about the systematic errors native
Japanese speakers make when pronouncing Mandarin Chinese.

- **Error Coding Dictionary (ECD)**: 31 error types in four dimensions (initials, finals, tones, prosody).
  Each entry has a stable code (e.g. `INIT-001`), the target sound and the error (pinyin and IPA), the
  proposed cause, where it occurs, whether it concerns production or perception, an **evidence grade
  A–D**, an evidence summary and its sources.
- **Error Mapping Table (EMT)**: the dictionary mapped onto every Mandarin syllable: 410 toneless and
  1,295 toned syllables, plus a separate layer for the neutral tone.
- Built from 23 studies, each checked against the original text. 16 of the 31 types are supported by at
  least two independent empirical studies (grade A); 9 rest on teaching observation or inference
  (grades C and D) and should be treated as hypotheses.

## Repository layout

**The knowledge base itself is in [`data/`](data/).** Everything else is the query tool, documentation and license.

```text
data/                         the knowledge base
  excel/                      Excel workbooks with the same content, mainly for viewing (Chinese headers, filters)
    错误编码字典_ECD.xlsx       error dictionary: all fields, grade definitions, references, IPA guide
    错误映射表_EMT.xlsx         mapping table: toned and toneless syllables, neutral tone, notes
  ecd.json / ecd.csv          dictionary: 31 error types, 22 fields each
  emt_toned.json / .csv       mapping table: 1,295 toned syllables
  emt_base.json / .csv        mapping table: 410 toneless syllables (initials and finals only)
  neutral_tone_layer.*        9 contexts of the neutral tone
  references.json             the 23 cited works
  phonetic_guide.csv          IPA symbols used
src/ja_mandarin_errors/       Python query tool (by pinyin, Chinese characters or code)
scripts/validate_data.py      consistency check of the data
tests/                        automated tests
LICENSE, CITATION.cff, CHANGELOG.md, pyproject.toml
```

The Excel workbooks and the JSON/CSV files are the same knowledge base in different formats: the workbooks are for
reading and looking things up by eye, the JSON and CSV files are for programs.

## 30-second start

**No programming.** Download [`data/excel/错误映射表_EMT.xlsx`](data/excel/错误映射表_EMT.xlsx) (look up a
syllable: filter the 音节 "syllable" column by pinyin with a tone number, e.g. `shu1`, `nv3`) and
[`data/excel/错误编码字典_ECD.xlsx`](data/excel/错误编码字典_ECD.xlsx) (each error type in full). The Excel files have
Chinese headers; rows containing a grade-D entry are shaded pink. For R or pandas use the CSV files in `data/`,
which have English headers; JSON versions with the same content are next to them.

**Python** (3.10+, no dependencies; `[text]` adds `pypinyin` for looking up Chinese characters):

```bash
pip install "ja-mandarin-errors[text] @ git+https://github.com/subarasi520/ja-mandarin-pronunciation-errors"
ja-mandarin-errors jiā 书 INIT-001 --lang en
```

```text
jia1
  INIT-003  B  Unaspirated affricate: tends to be produced as a Japanese voiced sound (ざ, じ)
  INIT-008  A  zh, ch, sh are hard to tell apart from j, q, x by ear
  FINA-006  B  Medial i tends to merge into the initial and disappear (as in Japanese palatalized syllables, e.g. jia pronounced like「チャー」)
  TONE-002  A  Tone 1: tends to start too low and fall at the end
书 shu1
  INIT-001  A  Retroflex: the tongue tip tends to be raised too little and the place moves forward (sh is often heard as x)
  ...
```

```python
from ja_mandarin_errors import KnowledgeBase

kb = KnowledgeBase()
kb.syllable("nǚ")                    # also "nv3", "nü3", "nu:3"; no tone = toneless table; tone 5 = neutral
kb.entry("TONE-001")                 # full dictionary entry
kb.entries(grade="A", category="tone")
kb.text("你好")                      # per character (needs pypinyin)
kb.reference("邓丹 2014")             # full citation of a source
```

**Any other language.** Read the JSON directly, for example in JavaScript:

```js
const url = "https://raw.githubusercontent.com/subarasi520/ja-mandarin-pronunciation-errors/main/data/emt_toned.json";
const emt = await (await fetch(url)).json();
console.log(emt.syllables["jia1"].entries);   // [{code, grade, note_zh, note_en}, ...]
```

## What is in `data/`

| File | Content |
|---|---|
| `excel/*.xlsx` | the dictionary and the mapping table as Excel workbooks (Chinese headers, filters) |
| `ecd.json` / `ecd.csv` | 31 entries, all fields; grade definitions; field notes |
| `emt_toned.json` / `emt_toned.csv` | 1,295 toned syllables (`jia1`, `nv3` …) with tone-marked pinyin, common example characters, and the entries with grade and a short note (Chinese and English) |
| `emt_base.json` / `emt_base.csv` | 410 toneless syllables → initial and final entries only |
| `neutral_tone_layer.json` / `.csv` | 9 contexts where the neutral tone occurs (particles, suffixes, reduplication …) |
| `references.json` | the 23 cited works |
| `phonetic_guide.csv` | the IPA symbols used |

Syllable keys are pinyin with a tone number; ü is written `v`. m, n and ng are interjection syllables and
carry no entries. Seven entries that act on all tones or above the syllable (`TONE-006`, `TONE-008`,
`PROS-001`–`004`, and `FINA-008` for erhua) are not listed per syllable; see `not_listed_per_syllable`
in the EMT JSON.

**Evidence grades**

| Grade | Meaning |
|---|---|
| A | At least two independent empirical studies of native Japanese speakers agree |
| B | One empirical study of native Japanese speakers |
| C | Teaching observation or textbook analysis only |
| D | Contrastive inference only, or contradicted by existing studies |

Only studies of native Japanese speakers count toward the grade; several papers reporting the same data
count once. Empirical means acoustic or articulatory measurement, a perception experiment, or production
rated by native listeners.

**Languages.** Names are given in Chinese, English and Japanese; descriptions and the per-syllable notes
in Chinese and English. Evidence summaries, causes and contexts are in Chinese. Where the two differ, the
Chinese text is authoritative.

## Ideas for use

**Teaching** (free for non-profit teaching)

- Look up the new words of a lesson before class and see which syllables to listen for.
- Focus on what is best supported: tones, aspiration, retroflex vs alveolo-palatal sibilants, u, e, ü and
  nasal codas. Grade C and D entries are worth watching rather than drilling.
- The `modality` field says whether a problem lies in production or perception. Aspiration of stops is a
  production problem (learners identify it almost without error), so practise speaking; zh/ch/sh vs
  j/q/x is confused in both, so listening practice can come first.
- Build minimal pairs (zhī–jī, shū–xū) and dictation items from the mapping table.

**Research** (free for non-commercial research)

- **Design experiments.** Pick stimuli where well-supported errors meet, for example syllables with
  `INIT-001` and `INIT-008` (zh/ch/sh vs j/q/x), or minimal pairs for a perception test.
- **Test the open hypotheses.** The nine C and D entries say exactly what has not been shown yet; a
  learner speech corpus can confirm or reject them one by one, and add frequencies the table does not have.
- **Code learner data the same way.** Using the ECD codes as error categories makes results from different
  studies comparable.
- **Study teaching materials.** Count which graded errors the vocabulary of a course or textbook touches
  and compare materials on that basis.
- **Compare first languages.** The fields and grading rules carry over to learners with other first
  languages; some errors here (tone 2 / tone 3 confusion) are known not to be specific to Japanese
  speakers.
- **Computational studies of L2 speech.** Codes and the syllable mapping are machine-readable and can be
  used as structured prior knowledge.

**Commercial development** (needs a separate license; please get in touch)

- Textbooks and publishers: pronunciation units, teaching order, exercises and tests for Japanese learners.
- Language schools and online courses: course design, placement and diagnostic tests, teacher training.
- Learning apps: per-word hints on likely errors, targeted minimal-pair and listening exercises.
- Speech technology: test sets and test cases tailored to native Japanese users, checked syllable by syllable.

## Read before use

- The table shows which errors **may** occur on a syllable, not how often. A long list for a syllable does
  not mean it is the hardest one.
- Everything comes from published studies and teaching observations; no new speech data were collected.
  Most studies had fewer than 30 participants, and the literature search was not a formal systematic review.
- Grade C and D entries (marked `has_grade_d` in the mapping) are hypotheses.
- Syllables are looked up in their citation tone; tone sandhi is not applied. `kb.text()` relies on
  `pypinyin`, which can pick the wrong reading of a polyphonic character.
- Some evidence concerns people who have never learned Chinese, some errors fade with study, and some
  show up in production but not in perception. The `modality` field and the evidence summaries say which.

## How to cite

See [CITATION.cff](CITATION.cff) (GitHub shows a “Cite this repository” button).

## License and contact

**Copyright**: the knowledge base (the data in `data/`) and the documentation and code in this repository are the personal property of the researchers of this study.

Free for **non-commercial research and non-profit teaching** only. Commercial use, use by companies, and
use in commercial courses, textbooks or apps need a separate written license; see [LICENSE](LICENSE).

**Contact:** open an issue in this repository titled “License inquiry”, or reach the maintainer through
the GitHub profile [@subarasi520](https://github.com/subarasi520).

Corrections are welcome: if an entry misreads a study, please open an issue with the page or table of the
original.
