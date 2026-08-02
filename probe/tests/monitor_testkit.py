"""
Shared no-network test scaffolding for the monitor tests (not collected by
pytest: no test_ prefix). Style and machinery follow convergence/tests:
requests.post is replaced with a recording fake for every path; any stray
network attempt or exhausted script fails loudly.
"""

import os
import sys
import json

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "harness"))
sys.path.insert(0, os.path.join(REPO, "probe", "monitor"))

import monitor  # noqa: E402
from convergence import providers  # noqa: E402

TESTKEY = "TESTKEY-fake-key-material-never-real"
ECHO = "echo-under-test"


def make_item(iid):
    """A test item whose decision text carries a unique marker so the fake
    post can route each request to its per-item script."""
    return {"id": iid,
            "decision": "ITEM {} scenario. A: a. B: b. C: c. D: d.".format(iid),
            "cell": "derivable"}


def make_model(mid="monitor-model-under-test"):
    return {"model": mid, "provider": "anthropic", "arms": ["A"],
            "host": None, "temperature_mode": "omit"}


class _Resp:
    status_code = 200

    def __init__(self, payload):
        self._payload = payload

    def json(self):
        return self._payload


class ScriptedPost:
    """Stands in for requests.post. Answer letters are scripted per item id
    and consumed in call order (run1 pops the first K, run2 the next K, and
    so on); echoes are optionally scripted per call for the tripwire tests.
    Records every call; an exhausted or unmatched script raises loudly."""

    def __init__(self, scripts, echo=ECHO, echo_seq=None):
        self.scripts = {iid: list(vals) for iid, vals in scripts.items()}
        self.echo = echo
        self.echo_seq = list(echo_seq or [])
        self.calls = []

    def __call__(self, url, headers=None, data=None, timeout=None):
        body = json.loads(data)
        prompt = body["messages"][0]["content"]
        matched = [iid for iid in self.scripts
                   if "ITEM {} scenario".format(iid) in prompt]
        if len(matched) != 1:
            raise AssertionError("prompt matched items %r" % matched)
        letters = self.scripts[matched[0]]
        if not letters:
            raise AssertionError("script exhausted for item %s" % matched[0])
        letter = letters.pop(0)
        echo = self.echo_seq.pop(0) if self.echo_seq else self.echo
        self.calls.append((matched[0], letter, echo))
        return _Resp({"content": [{"type": "text", "text": "ANSWER: " + letter}],
                      "model": echo})


class EnvGuard:
    """Remove some env vars, set others, restore everything on exit."""

    def __init__(self, remove=(), set_vars=None):
        self.remove = remove
        self.set_vars = set_vars or {}
        self.saved = {}

    def __enter__(self):
        for k in list(self.remove) + list(self.set_vars):
            self.saved[k] = os.environ.pop(k, None)
        for k, v in self.set_vars.items():
            os.environ[k] = v
        return self

    def __exit__(self, *exc):
        for k, v in self.saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


class Patched:
    """Install a ScriptedPost and the anthropic test key; restore on exit."""

    def __init__(self, post):
        self.post = post

    def __enter__(self):
        self._orig = providers.requests.post
        providers.requests.post = self.post
        self._env = EnvGuard(set_vars={"ANTHROPIC_API_KEY": TESTKEY})
        self._env.__enter__()
        return self.post

    def __exit__(self, *exc):
        providers.requests.post = self._orig
        self._env.__exit__(*exc)


def read_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]
