Handoff: add --probe-sampling to the convergence runner

Context. The pre-registration (Voids, sampling-variance probe) commits
to an empirical non-greedy sampling check at smoke: one fixed
open-ended prompt, three calls per model per arm, byte-identical
outputs across all three fail that model for that arm. models.json is
fully pinned as of 2c89d66; the temperature rule is in the file's
comment block and in PRE_REGISTRATION_CONVERGENCE.md. Nothing outside
convergence/ may change.

Behavior. A --probe-sampling flag on convergence/collect.py. For every
model in models.json and every arm it lists, issue the probe prompt
three times using the exact request shaping of that model and arm:
same adapter, same reasoning-off or reasoning-on configuration, same
temperature_mode, same retry sender. The probe prompt is this literal,
pinned byte-for-byte like the vendor_access prompt:

  "In two or three sentences, describe an imaginary small town,
  including its name and one notable landmark."

Comparison runs on the parsed answer text exactly as parse_response
returns it. Verdicts per model per arm: VARIED when any two of the
three outputs differ at byte level; DEGENERATE when all three are
byte-identical; ERROR when any call fails after retries, reported
without a verdict rather than folded into either state. DEGENERATE or
ERROR anywhere exits nonzero. google Arm A raises at request-build
time exactly as collection does; probe only the arms the entry lists.

Credentials. Identical fail-closed behavior to collection: every
required env var read before the first call, a missing one names
itself and issues zero requests. GOOGLE_API_KEY per 4df23d1, not
GEMINI_API_KEY.

Output. A human-readable report to stdout: per model per arm, the
verdict and the three output lengths. Full probe outputs written to a
timestamped file under convergence/probe_reports/, gitignored, so a
DEGENERATE verdict can be investigated without rerunning. No key
material anywhere on disk. Probe calls write no collection rows and
touch no collection output paths. Investigation guidance for
DEGENERATE: consider provider-side response caching of identical
requests before concluding greedy decoding.

Tests. No-network fixture tests in the existing style, added to
convergence/tests/: the probe prompt literal is byte-pinned; request
shaping per provider per arm matches the collection fixtures;
verdict logic covers VARIED, DEGENERATE, ERROR, including two-same-
one-different resolving to VARIED; credential fail-closed naming;
exit codes. Existing 10 test files must pass unmodified.

Deviations. Any departure from this spec is listed in the handoff
report. Undisclosed deviations are the failure mode this project
exists to study; do not add a sixth.
