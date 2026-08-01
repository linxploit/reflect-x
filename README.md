<div align="center">

```
 ██████╗ ███████╗███████╗██╗     ███████╗ ██████╗████████╗██╗  ██╗
 ██╔══██╗██╔════╝██╔════╝██║     ██╔════╝██╔════╝╚══██╔══╝╚██╗██╔╝
██████╔╝█████╗  █████╗  ██║     █████╗  ██║        ██║    ╚███╔╝
██╔══██╗██╔══╝  ██╔══╝  ██║     ██╔══╝  ██║        ██║    ██╔██╗
 ██║  ██║███████╗██║     ███████╗███████╗╚██████╗   ██║   ██╔╝ ██╗
 ╚═╝  ╚═╝╚══════╝╚═╝     ╚══════╝╚══════╝ ╚═════╝   ╚═╝   ╚═╝  ╚═╝
```

### Safe XSS Reflection Analyzer 

**No payloads fire. No JavaScript executes. Signal only.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![Made by Mindless](https://img.shields.io/badge/Made%20by-Mindless-ff69b4.svg)](https://linxploit.com/founder)
[![Linxploit](https://img.shields.io/badge/Linxploit-linxploit.com-black.svg)](https://linxploit.com)

**Made by [Mindless](https://linxploit.com/founder) — Founder & CEO of [Linxploit](https://linxploit.com)**

</div>

---

## 🧠 What is ReflectX?

**ReflectX** is a lightweight, safe reflection-analysis tool for web parameters. It sends a unique, harmless marker string to a target parameter and checks whether — and *how* — that marker comes back in the HTTP response.

It never constructs a real XSS payload, never runs a browser, and never executes JavaScript. Reflection is treated as a **signal that deserves manual follow-up**, not proof of a vulnerability — and ReflectX is upfront about that at every step.

This is a **triage** tool: it helps you quickly narrow down which parameters, across which targets, are worth a deeper manual XSS review — before you reach for a heavier scanner or a browser-based tool.

---

## ✨ Features

- 🎨 **Ultra-clean ASCII UI** — gradient banner, boxed panels, colorized risk tables, and a live progress readout, all rendered in the terminal with zero external UI dependencies.
- 🧪 **Safe-by-design testing** — every request uses a randomized, non-executable marker (`rfx_<random>_test`); no `<script>`, no `javascript:`, no event handlers are ever sent by default.
- 🧭 **Context-aware detection** — classifies where a reflection lands: raw HTML body, HTML attribute, `<script>` block, or HTML comment.
- 🔍 **Encoding awareness** — distinguishes between a **raw** reflection (highest risk), a **partially transformed** reflection, and a properly **HTML/URL-encoded** reflection (low risk).
- 🧬 **Optional probe characters** — `--probe-chars` appends safe, non-executable encoding-sensitive characters (`' " < > &`) to reveal whether the target actually encodes special characters, without ever sending real attack syntax.
- ⚡ **Concurrent scanning** — scan a single URL or an entire list of targets in parallel with configurable thread count.
- 🌐 **GET & POST support** — test query parameters or form fields.
- 🔐 **Custom headers, cookies & SSL control** — authenticate to the target the same way your browser would.
- 📊 **Exportable reports** — save full results as structured **JSON** or **CSV** for later review or integration into other tooling.
- 🛡️ **Authorization gate** — ReflectX asks for explicit confirmation that you're authorized to test a target before it sends a single request (skippable with `--yes` for automated/CI use on your own infrastructure).
- 🧩 **Zero heavy dependencies** — just `requests` and `colorama`.

---

## 📸 Preview

```
                   ✦ Safe XSS Reflection Analyzer ✦
       v2.0.0 · No payloads fire. No JS executes. Signal only.

╔══════════════════════════════════════════════════════╗
║                        ABOUT                          ║
╠══════════════════════════════════════════════════════╣
║ ● Author   : Mindless  (Linxploit — Founder & CEO)     ║
║ ● Website  : https://linxploit.com                     ║
║ ● Portfolio: https://linxploit.com/founder             ║
╚══════════════════════════════════════════════════════╝

═══ ➤ SCANNING 2 TARGET(S) ══════════════════════════════
  method=GET  param=q  threads=5  timeout=10s

[✘  HIGH ] https://target.example/search (param: q)
          ├─ status: 200   time: 84.2 ms
          ├─ reflection: RAW   context: html_body
          └─ snippet: <p>Result: rfx_a91kd8_test</p>

[✔  SAFE ] https://target.example/api (param: q)
          ├─ status: 200   time: 61.5 ms
          └─ no reflection detected

═══ ✦ SCAN SUMMARY ══════════════════════════════════════
  ✘ High risk (raw reflection)    :   1  ●
  ⚠ Medium risk (partial match)   :   0
  ⚠ Low risk (encoded reflection) :   0
  ✔ Safe (no reflection)          :   1  ●
  ! Errors                        :   0
════════════════════════════════════════════════════════════
  Total targets scanned: 2
  ⚑ Review HIGH risk targets manually before disclosure.
```

---

## 📦 Installation

```bash
git clone https://github.com/linxploit/reflectx.git
cd reflectx
pip install -r requirements.txt
```

Requires **Python 3.8+**.

---

## 🚀 Usage

### Scan a single URL

```bash
python3 reflectx.py -u "https://example.com/search" -p q
```

### Scan a list of targets

```bash
python3 reflectx.py -l examples/targets.txt -p q --threads 10
```

### Test a POST parameter

```bash
python3 reflectx.py -u "https://example.com/api/lookup" -p name -X POST
```

### Add authentication headers or cookies

```bash
python3 reflectx.py -u "https://example.com/dashboard" -p query \
  -H "Authorization: Bearer <token>" \
  -b "session=abc123; theme=dark"
```

### Reveal encoding behavior with safe probe characters

```bash
python3 reflectx.py -u "https://example.com/search" -p q --probe-chars -v
```

### Save a report

```bash
python3 reflectx.py -l examples/targets.txt -p q -o report.json
python3 reflectx.py -l examples/targets.txt -p q -o report.csv
```

### Skip the authorization prompt (for your own automated pipelines)

```bash
python3 reflectx.py -u "https://example.com/search" -p q --yes
```

### Full option reference

```bash
python3 reflectx.py --help
```

| Flag | Description |
|---|---|
| `-u`, `--url` | Single target URL |
| `-l`, `--list` | File with one target URL per line |
| `-p`, `--param` | Parameter name to inject the marker into (default: `q`) |
| `-X`, `--method` | `GET` or `POST` (default: `GET`) |
| `-t`, `--timeout` | Request timeout in seconds (default: `10`) |
| `--threads` | Concurrent worker threads (default: `5`) |
| `-H`, `--header` | Custom header `"Key: Value"`, repeatable |
| `-b`, `--cookies` | Cookie string `"a=1; b=2"` |
| `--no-verify-ssl` | Disable SSL certificate verification |
| `-o`, `--output` | Save report to `.json` or `.csv` |
| `-v`, `--verbose` | Show response snippets around reflections |
| `--probe-chars` | Append safe encoding-sensitive characters for deeper analysis |
| `--yes` | Skip the authorization confirmation prompt |
| `--no-banner` | Suppress the ASCII banner |
| `--version` | Print version info and exit |

---

## 🧭 How risk levels are determined

| Risk | Meaning |
|---|---|
| **HIGH** | Marker reflected **raw**, unescaped, in the response |
| **MEDIUM** | Marker reflected in a **transformed/partial** form |
| **LOW** | Marker reflected but properly **HTML/URL-encoded** |
| **SAFE** | Marker not found anywhere in the response |
| **ERROR** | The request itself failed (timeout, connection error, SSL error, etc.) |

> ⚠️ **Reflection is a signal, not a verdict.** A HIGH result means the input path is worth a manual, careful look — it does not by itself confirm an exploitable XSS vulnerability. Always validate manually before reporting or acting on results.

---

## ⚖️ Responsible use

ReflectX is built for **authorized security testing only** — your own applications, or targets you have explicit written permission to test (bug bounty scope, pentest engagement, CTF, staging environment, etc.).

- ReflectX **never** sends `<script>` tags, `javascript:` URIs, event-handler payloads, or any construct capable of executing code.
- ReflectX will ask you to confirm authorization before scanning, every time, unless you explicitly pass `--yes`.
- You are solely responsible for how you use this tool and for complying with all applicable laws and the terms of any authorization you've been granted.

---

## 🛠️ Project structure

```
reflectx/
├── reflectx.py          # Main executable — the tool itself
├── requirements.txt      # Python dependencies
├── examples/
│   └── targets.txt       # Example target list for -l/--list
├── LICENSE               # MIT License
└── README.md             # You are here
```

---

## 🤝 Contributing

Issues and pull requests are welcome. If you're proposing a new detection technique, please keep it in line with ReflectX's safe-by-design philosophy — no additions that construct or send executable payloads.

---

## 📜 License

Released under the [MIT License](LICENSE).

---

<div align="center">

### Made by **Mindless**
**Founder & CEO of [Linxploit](https://linxploit.com)**

🌐 [linxploit.com](https://linxploit.com) &nbsp;·&nbsp; 👤 [linxploit.com/founder](https://linxploit.com/founder)

</div>
