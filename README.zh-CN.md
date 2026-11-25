# 日语母语者普通话发音系统性偏误知识库

[English](README.md) · [日本語](README.ja.md) · 版本 2.1.0 · **非商业许可：限研究与非营利教学**（[LICENSE](LICENSE)）

把已发表研究中关于日语母语者普通话发音系统性偏误的结论，整理成带证据等级的结构化知识库。

- **《错误编码字典》（ECD）**：31 类偏误，分声母、韵母、声调、语流节律四个维度。每条有固定编码（如 `INIT-001`）、
  目标音与偏误表现（拼音和国际音标）、成因、出现环境、层面（产出或感知）、**A–D 证据等级**、证据摘要和文献。
- **《错误映射表》（EMT）**：把字典落实到普通话的每个音节上——410 个基础音节、1295 个带调音节，轻声另设一层。
- 依据 23 项研究，每项都对照原文核过。31 类中，16 类有两项以上相互独立的实证研究一致支持（A 级）；
  9 类只有教学观察或推断（C、D 级），应当作待检验的假设看待。

## 30 秒开始

**只要数据**：下载 [`data/ecd.csv`](data/ecd.csv) 和 [`data/emt_toned.csv`](data/emt_toned.csv)，
用 Excel、R 或 pandas 打开即可；同目录下有内容相同的 JSON。

**Python**（3.10 以上，无依赖；`[text]` 会装上 `pypinyin`，用于按汉字查询）：

```bash
pip install "ja-mandarin-errors[text] @ git+https://github.com/subarasi520/ja-mandarin-pronunciation-errors"
ja-mandarin-errors jiā 书 INIT-001
```

```text
jia1
  INIT-003  B  不送气塞擦音：易发成日语浊音ざ、じ一类
  INIT-008  A  听辨时 zh、ch、sh 与 j、q、x 难以分辨
  FINA-006  B  介音 i 易并入声母而脱落（拗音化，如 jia 读成「チャー」）
  TONE-002  A  阴平：起点易不够高、后段下滑
书 shu1
  INIT-001  A  翘舌音：舌尖易翘得不够，发音部位前移（sh 常被听成 x）
  ……
```

```python
from ja_mandarin_errors import KnowledgeBase

kb = KnowledgeBase()
kb.syllable("nǚ")                    # 也可写 "nv3"、"nü3"、"nu:3"；不带调查基础音节表；5 声＝轻声
kb.entry("TONE-001")                 # 字典条目全文
kb.entries(grade="A", category="tone")
kb.text("你好")                      # 逐字查询（需要 pypinyin）
kb.reference("邓丹 2014")             # 文献全称
```

**其他语言**：直接读 JSON，例如 JavaScript：

```js
const url = "https://raw.githubusercontent.com/subarasi520/ja-mandarin-pronunciation-errors/main/data/emt_toned.json";
const emt = await (await fetch(url)).json();
console.log(emt.syllables["jia1"].entries);   // [{code, grade, note_zh, note_en}, ...]
```

## `data/` 里有什么

| 文件 | 内容 |
|---|---|
| `ecd.json` / `ecd.csv` | 31 个条目的全部字段；证据等级定义；字段说明 |
| `emt_toned.json` / `emt_toned.csv` | 1295 个带调音节（`jia1`、`nv3`……）→ 条目、等级和简短说明（中、英） |
| `emt_base.json` / `emt_base.csv` | 410 个基础音节 → 只列声母、韵母条目 |
| `neutral_tone_layer.json` / `.csv` | 轻声出现的 9 类环境（助词、后缀、重叠式等） |
| `references.json` | 23 项文献 |
| `phonetic_guide.csv` | 所用国际音标的说明 |

音节键是带数字声调的拼音，ü 写作 `v`。m、n、ng 是叹词音节，不列条目。作用于全部声调或音节以上层面的 7 个条目
（`TONE-006`、`TONE-008`、`PROS-001`～`004`、儿化 `FINA-008`）不逐音节列出，见映射表 JSON 的 `not_listed_per_syllable`。

**证据等级**

| 等级 | 含义 |
|---|---|
| A | 至少两项以日语母语者为对象、相互独立的实证研究支持，主要结论一致 |
| B | 只有一项以日语母语者为对象的实证研究 |
| C | 只有教学观察或教材分析 |
| D | 只依据日汉对比推断，或已有文献提供了反证 |

评级只计以日语母语者为对象的研究；同一批数据发表的几篇只算一项。实证研究指声学或发音测量、感知实验，以及由母语者评判的产出实验。

**语言**：名称有中、英、日三种；说明和逐音节的简短说明有中、英两种；证据摘要、成因、出现环境只有中文。两种语言不一致时以中文为准。

## 用法的启发

- **设计实验**：挑出几类证据充分的偏误交汇的音节作刺激，例如同时带 `INIT-001` 和 `INIT-008` 的音节（zh/ch/sh 与 j/q/x），或做感知测试的最小对立对。
- **检验待验证的条目**：9 个 C、D 级条目写明了哪些还没有证据；用学习者语料可以逐条证实或否定，并补上映射表没有的频率。
- **用同一套编码分析学习者数据**：以 ECD 编码作偏误类别，不同研究的结果就能对照。
- **研究教材**：统计某门课或某本教材的词汇涉及哪些等级的偏误，以此比较不同教材。
- **比较不同母语背景**：字段和评级规则可以搬到其他母语背景的学习者上；其中有的偏误（阳平与上声相混）已知并非日语母语者特有。
- **二语语音的计算研究**：编码和音节映射都可以由程序直接读取，作为结构化的先验知识。
- **非营利教学**：查一课生词涉及的音节，看看要留意哪些证据充分的偏误；C、D 级条目适合留心观察，不必专门操练。

## 使用前请读

- 映射表说的是某个音节上**可能**出现哪些偏误，不是出现的频率。条目多的音节不等于最难的音节。
- 全部内容来自已发表的研究和教学观察，没有采集新的语音数据；多数研究的被试不到 30 人；文献收集没有按系统综述的规程进行。
- C、D 级条目（映射表中 `has_grade_d`）是待检验的假设。
- 音节按本调查询，不做变调处理；`kb.text()` 依赖 `pypinyin` 注音，多音字可能注错。
- 有的证据来自没有学过汉语的人，有的偏误随学习减轻，有的只在产出而不在感知中出现。见 `modality` 字段和证据摘要。

## 引用

见 [CITATION.cff](CITATION.cff)（GitHub 页面右侧有 “Cite this repository” 按钮）。

## 许可与联系方式

**仅限非商业研究和非营利教学**免费使用。商业用途、企业使用，以及用于商业课程、教材或应用，须另行取得书面授权，详见 [LICENSE](LICENSE)。

**联系方式**：在本仓库开一个标题为 “License inquiry” 的 issue，或通过 GitHub 主页 [@subarasi520](https://github.com/subarasi520) 联系维护者。

欢迎指正：如果某条对原文理解有误，请开 issue 并注明原文的页码或表格。
