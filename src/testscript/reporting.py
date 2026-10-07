"""Standalone, escaped reports from the runner's event model."""

import json
import xml.etree.ElementTree as ET
from dataclasses import asdict
from datetime import UTC, datetime
from html import escape
from pathlib import Path


def write_reports(results, directory):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    counts = {state: sum(r.status == state for r in results) for state in ("passed", "failed", "skipped")}
    data = {
        "version": "0.1.0",
        "generated": datetime.now(UTC).isoformat(),
        "summary": counts,
        "tests": [asdict(r) for r in results],
    }
    (directory / "results.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    suite = ET.Element(
        "testsuite",
        name="TestScript",
        tests=str(len(results)),
        failures=str(counts["failed"]),
        skipped=str(counts["skipped"]),
        time=f"{sum(r.duration for r in results):.6f}",
    )
    for result in results:
        case = ET.SubElement(
            suite,
            "testcase",
            name=result.name,
            classname=Path(result.path).stem,
            time=f"{result.duration:.6f}",
        )
        if result.status == "failed":
            ET.SubElement(case, "failure", message=result.errors[0]).text = "\n".join(result.errors)
        elif result.status == "skipped":
            ET.SubElement(case, "skipped").text = next(
                (e["message"] for e in result.events if e["kind"] == "skip"), "Skipped"
            )
        ET.SubElement(case, "system-out").text = "\n".join(e["message"] for e in result.events)
    ET.ElementTree(suite).write(directory / "junit.xml", encoding="utf-8", xml_declaration=True)
    sections = []
    for result in results:
        events = []
        for event in result.events:
            message = escape(event["message"])
            if event["kind"] == "screenshot":
                message = f'<a href="{message}">Screenshot</a><img alt="Test evidence" src="{message}">'
            trail = escape(" / ".join(event.get("steps", [])))
            events.append(
                f"<li><span>{escape(event['kind'])}</span><div>{message}<small>{trail}</small></div></li>"
            )
        sections.append(
            f'<details class="{result.status}" {"open" if result.status == "failed" else ""}>'
            f"<summary><b>{escape(result.name)}</b><em>{result.status}</em>"
            f"<time>{result.duration:.3f}s</time></summary><ul>{''.join(events)}</ul></details>"
        )
    html = """<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>TestScript • execution report</title><style>
:root{color-scheme:dark}*{box-sizing:border-box}body{margin:0;background:#0b1016;color:#e5edf5;font:15px/1.6 system-ui}
main{max-width:1100px;margin:auto;padding:56px 24px}header{border-bottom:1px solid #273442;padding-bottom:28px;margin-bottom:32px}
h1{font-size:38px;letter-spacing:-1px;margin:12px 0}header small{color:#70e3c4;letter-spacing:3px}.counts{display:flex;gap:12px;flex-wrap:wrap}
.counts span{padding:8px 16px;background:#15212b;border:1px solid #273442;border-radius:9px}details{margin:12px 0;border:1px solid #273442;border-radius:12px;overflow:hidden}
summary{padding:20px;display:flex;gap:16px;align-items:center;cursor:pointer;background:#111a24}summary b{flex:1}em{font-style:normal;color:#70e3c4}
.failed em{color:#ff9393}.skipped em{color:#efd17c}time,small{color:#91a2b5}ul{padding:0 24px;list-style:none}li{display:flex;gap:16px;padding:12px 0;border-bottom:1px solid #23303c}
li>span{font:12px monospace;color:#91a2b5;min-width:80px}li div{min-width:0;overflow-wrap:anywhere}li small{display:block}img{max-width:100%;display:block;margin-top:12px;border-radius:8px}a{color:#70e3c4}
@media(max-width:600px){main{padding:28px 16px}summary{flex-wrap:wrap}li{display:block}}
</style><main><header><small>{ } TESTSCRIPT / EXECUTION</small><h1>Every step. One story.</h1><div class="counts">"""
    html += "".join(f"<span>{n} {state}</span>" for state, n in counts.items())
    html += f"</div></header>{''.join(sections)}<footer>TestScript 0.1.0</footer></main></html>"
    (directory / "report.html").write_text(html, encoding="utf-8")
    return directory / "report.html"
