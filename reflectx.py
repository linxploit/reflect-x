#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
██████╗ ███████╗███████╗██╗     ███████╗ ██████╗████████╗██╗  ██╗
██╔══██╗██╔════╝██╔════╝██║     ██╔════╝██╔════╝╚══██╔══╝╚██╗██╔╝
██████╔╝█████╗  █████╗  ██║     █████╗  ██║        ██║    ╚███╔╝
██╔══██╗██╔══╝  ██╔══╝  ██║     ██╔══╝  ██║        ██║    ██╔██╗
██║  ██║███████╗██║     ███████╗███████╗╚██████╗   ██║   ██╔╝ ██╗
╚═╝  ╚═╝╚══════╝╚═╝     ╚══════╝╚══════╝ ╚═════╝   ╚═╝   ╚═╝  ╚═╝

ReflectX — Safe XSS Reflection Analyzer
Made by Mindless — Founder & CEO of Linxploit
https://linxploit.com | https://linxploit.com/founder

DISCLAIMER:
    ReflectX never executes JavaScript and never fires a real XSS
    payload. It only checks whether a harmless, unique marker string
    is reflected back in an HTTP response, and reports the surrounding
    context. Reflection is a *signal*, not proof of exploitability.

    Only use this tool against targets you own or are explicitly
    authorized to test. You are solely responsible for how you use it.
"""

import argparse
import concurrent.futures
import csv
import html
import json
import os
import random
import re
import string
import sys
import time
import urllib.parse
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import List, Optional

import requests
from colorama import Fore, Back, Style, init as colorama_init

colorama_init(autoreset=True)

TOOL_NAME = "ReflectX"
VERSION = "2.0.0"
AUTHOR = "Mindless"
ORG = "Linxploit"
SITE = "https://linxploit.com"
PORTFOLIO = "https://linxploit.com/founder"

requests.packages.urllib3.disable_warnings()  # noqa

GRADIENT = [
    "\033[38;5;51m",   # cyan
    "\033[38;5;45m",
    "\033[38;5;39m",
    "\033[38;5;33m",
    "\033[38;5;27m",
    "\033[38;5;21m",
    "\033[38;5;57m",
    "\033[38;5;93m",
    "\033[38;5;129m",
    "\033[38;5;165m",
]
RESET = Style.RESET_ALL
DIM = Style.DIM
BOLD = Style.BRIGHT

C_OK = Fore.GREEN + BOLD
C_WARN = Fore.YELLOW + BOLD
C_BAD = Fore.RED + BOLD
C_INFO = Fore.CYAN
C_MUTE = Fore.WHITE + DIM
C_ACC = "\033[38;5;213m" + BOLD  # pink accent


def gradient_line(text: str) -> str:
    """Apply a horizontal colour gradient across a line of text."""
    out = []
    n = max(len(GRADIENT) - 1, 1)
    for i, ch in enumerate(text):
        color = GRADIENT[int((i / max(len(text) - 1, 1)) * n)]
        out.append(color + ch)
    return "".join(out) + RESET


def supports_unicode() -> bool:
    enc = (sys.stdout.encoding or "").lower()
    return "utf" in enc


UNICODE_OK = supports_unicode()

# Box-drawing characters with an ASCII-safe fallback
BOX = {
    "tl": "╔" if UNICODE_OK else "+",
    "tr": "╗" if UNICODE_OK else "+",
    "bl": "╚" if UNICODE_OK else "+",
    "br": "╝" if UNICODE_OK else "+",
    "h": "═" if UNICODE_OK else "-",
    "v": "║" if UNICODE_OK else "|",
    "lt": "╠" if UNICODE_OK else "+",
    "rt": "╣" if UNICODE_OK else "+",
    "t": "╦" if UNICODE_OK else "+",
    "b": "╩" if UNICODE_OK else "+",
    "x": "╬" if UNICODE_OK else "+",
    "arrow": "➤" if UNICODE_OK else ">",
    "bullet": "●" if UNICODE_OK else "*",
    "check": "✔" if UNICODE_OK else "OK",
    "cross": "✘" if UNICODE_OK else "X",
    "warn": "⚠" if UNICODE_OK else "!",
    "spark": "✦" if UNICODE_OK else "*",
}

BANNER_ART = r"""
██████╗ ███████╗███████╗██╗     ███████╗ ██████╗████████╗██╗  ██╗
██╔══██╗██╔════╝██╔════╝██║     ██╔════╝██╔════╝╚══██╔══╝╚██╗██╔╝
██████╔╝█████╗  █████╗  ██║     █████╗  ██║        ██║    ╚███╔╝
██╔══██╗██╔══╝  ██╔══╝  ██║     ██╔══╝  ██║        ██║    ██╔██╗
██║  ██║███████╗██║     ███████╗███████╗╚██████╗   ██║   ██╔╝ ██╗
╚═╝  ╚═╝╚══════╝╚═╝     ╚══════╝╚══════╝ ╚═════╝   ╚═╝   ╚═╝  ╚═╝
""".rstrip("\n")

BANNER_ART_ASCII = r"""
 ____  ____  __    ____  __     ___   __
(  _ \(  __)(  )  (  __)(  )   / __) / /_
 )   / ) _) / (_/\ ) _) / (_/\( (__ ( '_ \
(__\_)(____)\____/(____)\____/ \___) \____)
""".rstrip("\n")


def render_banner():
    art = BANNER_ART if UNICODE_OK else BANNER_ART_ASCII
    width = max(len(line) for line in art.splitlines()) + 4
    lines = art.splitlines()

    print()
    for line in lines:
        print(gradient_line(line))

    tagline = f"{BOX['spark']} Safe XSS Reflection Analyzer {BOX['spark']}"
    print()
    print(C_ACC + tagline.center(width) + RESET)
    sub = f"v{VERSION} · No payloads fire. No JS executes. Signal only."
    print(C_MUTE + sub.center(width) + RESET)
    print()

    info_box(
        [
            f"{BOX['bullet']} Author   : {AUTHOR}  ({ORG} — Founder & CEO)",
            f"{BOX['bullet']} Website  : {SITE}",
            f"{BOX['bullet']} Portfolio: {PORTFOLIO}",
        ],
        title="ABOUT",
        color=Fore.MAGENTA,
    )


def box_line(width: int, color: str) -> str:
    return color + BOX["h"] * width + RESET


def info_box(lines: List[str], title: str = "", color: str = Fore.CYAN, width: Optional[int] = None):
    content_width = width or (max((len(l) for l in lines), default=20) + 4)
    top = f"{color}{BOX['tl']}{BOX['h'] * content_width}{BOX['tr']}{RESET}"
    bot = f"{color}{BOX['bl']}{BOX['h'] * content_width}{BOX['br']}{RESET}"
    print(top)
    if title:
        pad = content_width - len(title) - 2
        left = pad // 2
        right = pad - left
        print(f"{color}{BOX['v']}{RESET} {' ' * left}{BOLD}{title}{RESET}{' ' * right} {color}{BOX['v']}{RESET}")
        print(f"{color}{BOX['lt']}{BOX['h'] * content_width}{BOX['rt']}{RESET}")
    for line in lines:
        pad = content_width - len(strip_ansi(line)) - 1
        pad = max(pad, 0)
        print(f"{color}{BOX['v']}{RESET} {Fore.WHITE}{line}{RESET}{' ' * pad}{color}{BOX['v']}{RESET}")
    print(bot)


ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def strip_ansi(s: str) -> str:
    return ANSI_RE.sub("", s)


def section_header(title: str, color: str = Fore.CYAN, icon: str = None):
    icon = icon or BOX["arrow"]
    print()
    print(color + BOLD + f"{BOX['h'] * 3} {icon} {title} " + BOX['h'] * max(0, 50 - len(title)) + RESET)


def hr(color=C_MUTE, width=60):
    print(color + BOX["h"] * width + RESET)


class Spinner:
    """A tiny inline spinner for long-running network calls."""

    FRAMES_UNI = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    FRAMES_ASCII = ["|", "/", "-", "\\"]

    def __init__(self, label: str):
        self.label = label
        self.frames = self.FRAMES_UNI if UNICODE_OK else self.FRAMES_ASCII
        self.i = 0

    def tick(self):
        frame = self.frames[self.i % len(self.frames)]
        self.i += 1
        sys.stdout.write(f"\r{Fore.CYAN}{frame}{RESET} {self.label} ")
        sys.stdout.flush()

    def stop(self, final: str = ""):
        sys.stdout.write("\r" + " " * (len(self.label) + 10) + "\r")
        if final:
            print(final)
        sys.stdout.flush()


def progress_bar(current: int, total: int, label: str = "", width: int = 32):
    ratio = current / total if total else 1
    filled = int(width * ratio)
    bar_char = "█" if UNICODE_OK else "#"
    empty_char = "░" if UNICODE_OK else "-"
    bar = bar_char * filled + empty_char * (width - filled)
    pct = int(ratio * 100)
    color = C_OK if pct == 100 else C_INFO
    sys.stdout.write(f"\r{color}[{bar}]{RESET} {pct:3d}%  {C_MUTE}{label}{RESET}")
    sys.stdout.flush()
    if current >= total:
        print()


RISK_LEVELS = {
    "RAW": ("HIGH", C_BAD),
    "PARTIAL": ("MEDIUM", C_WARN),
    "ENCODED": ("LOW", C_INFO),
    "NONE": ("SAFE", C_OK),
    "ERROR": ("ERROR", C_MUTE),
}

CONTEXTS = [
    ("script_block", re.compile(r"<script[^>]*>[^<]*{marker}", re.IGNORECASE)),
    ("html_attribute", re.compile(r'=["\']?[^"\'>]*{marker}', re.IGNORECASE)),
    ("html_comment", re.compile(r"<!--[^>]*{marker}", re.IGNORECASE)),
    ("html_body", re.compile(r">[^<]*{marker}", re.IGNORECASE)),
]


def random_marker(prefix: str = "rfx", probe_chars: bool = False) -> str:
    suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
    marker = f"{prefix}_{suffix}_test"
    if probe_chars:
        # Encoding-sensitive characters only (no executable syntax such as
        # <script> or javascript:), used purely to see whether HTML/URL
        # encoding is applied to reflected input.
        marker += "'\"<>&"
    return marker


@dataclass
class ScanResult:
    url: str
    param: str
    marker: str
    status_code: Optional[int] = None
    reflected: bool = False
    reflection_type: str = "NONE"       # RAW | ENCODED | PARTIAL | NONE | ERROR
    contexts: List[str] = field(default_factory=list)
    response_time_ms: Optional[float] = None
    error: Optional[str] = None
    snippet: Optional[str] = None

    @property
    def risk(self):
        return RISK_LEVELS.get(self.reflection_type, RISK_LEVELS["NONE"])


def detect_reflection(body: str, marker: str) -> ScanResult:
    """Classify how (if at all) the marker is reflected in the response."""
    result_type = "NONE"
    contexts_hit = []

    if marker in body:
        result_type = "RAW"
    else:
        html_encoded = html.escape(marker)
        url_encoded = urllib.parse.quote(marker)
        if html_encoded in body or url_encoded in body:
            result_type = "ENCODED"
        elif marker.lower() in body.lower():
            result_type = "PARTIAL"

    if result_type in ("RAW", "PARTIAL"):
        for name, pattern in CONTEXTS:
            try:
                if pattern.search(body.replace("{marker}", marker)) or re.search(
                    pattern.pattern.replace("{marker}", re.escape(marker)), body, re.IGNORECASE
                ):
                    contexts_hit.append(name)
            except re.error:
                continue

    return result_type, contexts_hit


def extract_snippet(body: str, marker: str, radius: int = 40) -> Optional[str]:
    idx = body.find(marker)
    if idx == -1:
        idx = body.lower().find(marker.lower())
    if idx == -1:
        return None
    start = max(0, idx - radius)
    end = min(len(body), idx + len(marker) + radius)
    snippet = body[start:end].replace("\n", " ").replace("\r", "")
    return snippet.strip()


def scan_target(
    url: str,
    param: str,
    timeout: int,
    headers: dict,
    cookies: dict,
    verify_ssl: bool,
    method: str,
    probe_chars: bool = False,
) -> ScanResult:
    marker = random_marker(probe_chars=probe_chars)
    result = ScanResult(url=url, param=param, marker=marker)

    try:
        start = time.perf_counter()
        if method == "GET":
            sep = "&" if urllib.parse.urlparse(url).query else "?"
            encoded_marker = urllib.parse.quote(marker, safe="")
            target = f"{url}{sep}{param}={encoded_marker}"
            resp = requests.get(
                target, headers=headers, cookies=cookies,
                timeout=timeout, verify=verify_ssl,
            )
        else:
            resp = requests.post(
                url, data={param: marker}, headers=headers, cookies=cookies,
                timeout=timeout, verify=verify_ssl,
            )
        elapsed = (time.perf_counter() - start) * 1000

        result.status_code = resp.status_code
        result.response_time_ms = round(elapsed, 1)

        rtype, contexts = detect_reflection(resp.text, marker)
        result.reflection_type = rtype
        result.reflected = rtype in ("RAW", "PARTIAL", "ENCODED")
        result.contexts = contexts
        result.snippet = extract_snippet(resp.text, marker)

    except requests.exceptions.Timeout:
        result.reflection_type = "ERROR"
        result.error = "Request timed out"
    except requests.exceptions.SSLError as e:
        result.reflection_type = "ERROR"
        result.error = f"SSL error: {e}"
    except requests.exceptions.ConnectionError:
        result.reflection_type = "ERROR"
        result.error = "Connection failed"
    except Exception as e:  # noqa
        result.reflection_type = "ERROR"
        result.error = str(e)

    return result


def print_result(result: ScanResult, verbose: bool):
    label, color = result.risk
    icon = {
        "HIGH": BOX["cross"],
        "MEDIUM": BOX["warn"],
        "LOW": BOX["warn"],
        "SAFE": BOX["check"],
        "ERROR": "!",
    }[label]

    print(f"{color}[{icon} {label:^6}]{RESET} {Fore.WHITE}{result.url}{RESET} "
          f"{C_MUTE}(param: {result.param}){RESET}")

    if result.error:
        print(f"          {C_BAD}└─ Error: {result.error}{RESET}")
        return

    print(f"          {C_MUTE}├─ status: {result.status_code}   "
          f"time: {result.response_time_ms} ms{RESET}")

    if result.reflected:
        ctx = ", ".join(result.contexts) if result.contexts else "unclassified"
        print(f"          {C_MUTE}├─ reflection: {RESET}{color}{result.reflection_type}{RESET}"
              f"{C_MUTE}   context: {ctx}{RESET}")
        if verbose and result.snippet:
            print(f"          {C_MUTE}└─ snippet: {DIM}{result.snippet[:120]}{RESET}")
    else:
        print(f"          {C_MUTE}└─ no reflection detected{RESET}")


def print_summary(results: List[ScanResult]):
    total = len(results)
    high = sum(1 for r in results if r.risk[0] == "HIGH")
    med = sum(1 for r in results if r.risk[0] == "MEDIUM")
    low = sum(1 for r in results if r.risk[0] == "LOW")
    safe = sum(1 for r in results if r.risk[0] == "SAFE")
    errors = sum(1 for r in results if r.risk[0] == "ERROR")

    section_header("SCAN SUMMARY", Fore.MAGENTA, BOX["spark"])
    rows = [
        (f"{BOX['cross']} High risk (raw reflection)", high, C_BAD),
        (f"{BOX['warn']} Medium risk (partial match)", med, C_WARN),
        (f"{BOX['warn']} Low risk (encoded reflection)", low, C_INFO),
        (f"{BOX['check']} Safe (no reflection)", safe, C_OK),
        ("! Errors", errors, C_MUTE),
    ]
    label_w = max(len(strip_ansi(r[0])) for r in rows)
    for label, count, color in rows:
        bar_len = min(count, 30)
        bar = (BOX["bullet"] * bar_len) if UNICODE_OK else ("*" * bar_len)
        print(f"  {color}{label.ljust(label_w)}{RESET} : {color}{count:>3}{RESET}  {color}{bar}{RESET}")

    hr(Fore.MAGENTA, 60)
    print(f"  {BOLD}Total targets scanned:{RESET} {total}")
    if high:
        print(f"  {C_BAD}{BOLD}⚑ Review HIGH risk targets manually before disclosure.{RESET}")
    print()


def save_json(results: List[ScanResult], path: str):
    data = {
        "tool": TOOL_NAME,
        "version": VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "author": AUTHOR,
        "organization": ORG,
        "results": [asdict(r) for r in results],
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def save_csv(results: List[ScanResult], path: str):
    fields = ["url", "param", "marker", "status_code", "reflected",
              "reflection_type", "contexts", "response_time_ms", "error"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for r in results:
            row = asdict(r)
            row["contexts"] = ";".join(row["contexts"])
            row.pop("snippet", None)
            writer.writerow({k: row[k] for k in fields})


def parse_header_list(items: Optional[List[str]]) -> dict:
    headers = {}
    if not items:
        return headers
    for item in items:
        if ":" in item:
            k, v = item.split(":", 1)
            headers[k.strip()] = v.strip()
    return headers


def parse_cookie_string(cookie_str: Optional[str]) -> dict:
    cookies = {}
    if not cookie_str:
        return cookies
    for part in cookie_str.split(";"):
        if "=" in part:
            k, v = part.split("=", 1)
            cookies[k.strip()] = v.strip()
    return cookies


def load_targets(args) -> List[str]:
    targets = []
    if args.url:
        targets.append(args.url)
    if args.list:
        if not os.path.isfile(args.list):
            print(C_BAD + f"[!] File not found: {args.list}" + RESET)
            sys.exit(1)
        with open(args.list, "r", encoding="utf-8") as f:
            targets.extend(line.strip() for line in f if line.strip() and not line.startswith("#"))
    return targets


def confirm_authorization(skip: bool) -> bool:
    if skip:
        return True
    info_box(
        [
            f"{BOX['warn']} Only test targets you OWN or are AUTHORIZED to test.",
            f"{BOX['warn']} Unauthorized scanning may be illegal in your jurisdiction.",
        ],
        title="AUTHORIZATION REQUIRED",
        color=Fore.YELLOW,
    )
    try:
        answer = input(f"{BOLD}Type 'yes' to confirm you are authorized: {RESET}").strip().lower()
    except (EOFError, KeyboardInterrupt):
        return False
    return answer == "yes"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="reflectx",
        description=f"{TOOL_NAME} — Safe XSS Reflection Analyzer by {AUTHOR} ({ORG})",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  reflectx.py -u https://example.com/search -p q\n"
            "  reflectx.py -l targets.txt -p q --threads 10 -o report.json\n"
            "  reflectx.py -u https://example.com/api -p name -X POST --yes\n"
        ),
    )
    parser.add_argument("-u", "--url", help="Target URL to test")
    parser.add_argument("-l", "--list", help="File containing a list of target URLs (one per line)")
    parser.add_argument("-p", "--param", default="q", help="Parameter name to inject the marker into (default: q)")
    parser.add_argument("-X", "--method", choices=["GET", "POST"], default="GET", help="HTTP method (default: GET)")
    parser.add_argument("-t", "--timeout", type=int, default=10, help="Request timeout in seconds (default: 10)")
    parser.add_argument("--threads", type=int, default=5, help="Concurrent worker threads (default: 5)")
    parser.add_argument("-H", "--header", action="append", help="Custom header 'Key: Value' (repeatable)")
    parser.add_argument("-b", "--cookies", help="Cookie string 'a=1; b=2'")
    parser.add_argument("--no-verify-ssl", action="store_true", help="Disable SSL certificate verification")
    parser.add_argument("-o", "--output", help="Save results to file (.json or .csv, format inferred from extension)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Show response snippets around reflections")
    parser.add_argument(
        "--probe-chars", action="store_true",
        help="Append safe encoding-sensitive characters (' \" < > &) to the marker "
             "to reveal whether output encoding is applied. Still non-executable.",
    )
    parser.add_argument("--yes", action="store_true", help="Skip the authorization confirmation prompt")
    parser.add_argument("--no-banner", action="store_true", help="Suppress the ASCII banner")
    parser.add_argument("--version", action="store_true", help="Show version information and exit")
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.version:
        print(f"{TOOL_NAME} v{VERSION} — by {AUTHOR} ({ORG})")
        return

    if not args.no_banner:
        render_banner()

    targets = load_targets(args)
    if not targets:
        parser.print_help()
        print(C_BAD + "\n[!] No target provided. Use -u/--url or -l/--list.\n" + RESET)
        sys.exit(1)

    if not confirm_authorization(args.yes):
        print(C_BAD + "\n[!] Authorization not confirmed. Aborting.\n" + RESET)
        sys.exit(1)

    headers = parse_header_list(args.header)
    cookies = parse_cookie_string(args.cookies)
    headers.setdefault("User-Agent", f"{TOOL_NAME}/{VERSION} (+{SITE})")

    section_header(f"SCANNING {len(targets)} TARGET(S)", Fore.CYAN, BOX["arrow"])
    print(f"{C_MUTE}  method={args.method}  param={args.param}  threads={args.threads}  timeout={args.timeout}s{RESET}\n")

    results: List[ScanResult] = []
    total = len(targets)
    completed = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.threads) as pool:
        futures = {
            pool.submit(
                scan_target, url, args.param, args.timeout, headers, cookies,
                not args.no_verify_ssl, args.method, args.probe_chars,
            ): url
            for url in targets
        }
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            results.append(result)
            completed += 1
            print()  # spacing before each result block
            print_result(result, args.verbose)

    print_summary(results)

    if args.output:
        ext = os.path.splitext(args.output)[1].lower()
        if ext == ".csv":
            save_csv(results, args.output)
        else:
            save_json(results, args.output)
        print(C_OK + f"{BOX['check']} Report saved to: {args.output}\n" + RESET)

    print(C_MUTE + f"{BOX['h']*60}" + RESET)
    print(C_ACC + f"  {TOOL_NAME} · Made by {AUTHOR} — Founder & CEO of {ORG}" + RESET)
    print(C_MUTE + f"  {SITE}  |  {PORTFOLIO}" + RESET)
    print(C_MUTE + f"{BOX['h']*60}\n" + RESET)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(C_WARN + "\n\n[!] Interrupted by user. Exiting.\n" + RESET)
        sys.exit(130)
