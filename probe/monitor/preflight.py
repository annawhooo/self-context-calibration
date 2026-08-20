"""Pre-flight credential check for the drift monitor.

Runs before the daily probe (its own scheduled task, 06:00, three hours
of lead) and answers one question per provider: does the key actually
WORK right now? check-env verifies variables are set; the August
outages showed that is not the failure mode that bites. The gpt outage
was a valid key with exhausted credits (429). The Claude outage was a
set-but-revoked key (401). Both pass check-env. Both fail here.

Method: one minimal real request per distinct roster provider, shaped
by the production request builder (convergence.providers.build_request,
the same path the monitor uses), sent once. HTTP 200 is a pass.
Retryable server statuses get one retry after 60 seconds so a transient
5xx does not page anyone at dawn. Everything else is a fail carrying
the status and the first line of the body, never any key material.

Alerting: on any failure, an email is sent if SCC_ALERT_EMAIL (to/from
address) and SCC_ALERT_SMTP_PASS (Gmail app password) are set at the
user level; otherwise the failure is stderr plus a nonzero exit and the
task log carries it. The email contains provider names and statuses
only. Exit codes: 0 all providers pass, 1 any fail, 2 configuration
problem (missing env var, unreadable roster).

--fresh-env overlays HKCU\\Environment values onto os.environ before
checking. This exists because a shell opened before a setx holds stale
variables (the exact mechanism of the August 19 outage: key rotated,
task environment never re-verified). The scheduled task resolves fresh
user env at launch anyway; the flag makes manual runs from old windows
tell the truth too.

Scheduling (documented in README.md, same pattern as the probe task):
  schtasks /Create /TN "scc-drift-preflight" /SC DAILY /ST 06:00 ...
This script never touches monitor.py, the bands, or any committed
record. It issues at most one tiny request per provider per run.
"""
import os
import sys
import json
import time
import argparse
import smtplib
from email.message import EmailMessage

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO)

import requests  # noqa: E402
from convergence.providers import PROVIDERS, build_request  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROSTER_PATH = os.path.join(HERE, "roster.json")
PROMPT = "Preflight connectivity check. Reply with the single word OK."
RETRYABLE = (500, 502, 503, 529)


def load_roster(path):
    with open(path, encoding="utf-8") as fh:
        doc = json.load(fh)
    return doc if isinstance(doc, list) else doc["models"]


def overlay_fresh_env():
    import winreg
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as key:
        i = 0
        while True:
            try:
                name, value, _ = winreg.EnumValue(key, i)
            except OSError:
                break
            os.environ[name] = str(value)
            i += 1


def check_provider(provider, model_cfg):
    env = PROVIDERS[provider]["env"]
    api_key = os.environ.get(env)
    if not api_key:
        return ("FAIL", "%s not set" % env)
    arm = (model_cfg.get("arms") or ["A"])[0]
    url, headers, body, _ = build_request(model_cfg, arm, PROMPT, api_key)
    for attempt in (1, 2):
        try:
            r = requests.post(url, headers=headers, data=json.dumps(body),
                              timeout=60)
        except requests.RequestException as exc:
            return ("FAIL", "request error: %s" % type(exc).__name__)
        if r.status_code == 200:
            return ("PASS", "http 200")
        if r.status_code in RETRYABLE and attempt == 1:
            time.sleep(60)
            continue
        snippet = " ".join(r.text.split())[:120]
        return ("FAIL", "http %d %s" % (r.status_code, snippet))
    return ("FAIL", "unreachable")


def send_alert(failures, results):
    to_addr = os.environ.get("SCC_ALERT_EMAIL")
    app_pass = os.environ.get("SCC_ALERT_SMTP_PASS")
    if not to_addr or not app_pass:
        sys.stderr.write(
            "alert email not configured (SCC_ALERT_EMAIL / "
            "SCC_ALERT_SMTP_PASS); failure reported by exit code only.\n")
        return False
    msg = EmailMessage()
    msg["Subject"] = "[scc-drift-monitor] preflight FAIL: " + ", ".join(
        sorted(failures))
    msg["From"] = to_addr
    msg["To"] = to_addr
    lines = ["Preflight credential check failed before today's 09:00 "
             "probe run.", ""]
    lines += ["  %-10s %-4s %s" % (p, s, d) for p, (s, d) in
              sorted(results.items())]
    lines += ["", "Fix the key(s), then verify: python "
              "probe\\monitor\\preflight.py --fresh-env",
              "The 09:00 probe will fail closed (ERROR verdicts) if "
              "this is not resolved."]
    msg.set_content("\n".join(lines))
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(to_addr, app_pass)
        smtp.send_message(msg)
    return True


def main(argv=None):
    ap = argparse.ArgumentParser(prog="preflight.py")
    ap.add_argument("--fresh-env", action="store_true",
                    help="overlay HKCU user environment before checking")
    ap.add_argument("--no-email", action="store_true",
                    help="report only; never attempt the alert email")
    args = ap.parse_args(argv)
    if args.fresh_env:
        overlay_fresh_env()
    try:
        roster = load_roster(ROSTER_PATH)
    except (OSError, ValueError, KeyError) as exc:
        sys.stderr.write("roster unreadable: %s\n" % exc)
        return 2
    by_provider = {}
    for m in roster:
        by_provider.setdefault(m["provider"], m)
    results = {}
    for provider, model_cfg in sorted(by_provider.items()):
        results[provider] = check_provider(provider, model_cfg)
        print("%-10s %-4s %s" % (provider, results[provider][0],
                                 results[provider][1]))
    failures = [p for p, (s, _) in results.items() if s != "PASS"]
    if failures:
        if not args.no_email:
            try:
                send_alert(failures, results)
            except Exception as exc:  # alert failure must not mask the check
                sys.stderr.write("alert email failed: %s\n" % exc)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
