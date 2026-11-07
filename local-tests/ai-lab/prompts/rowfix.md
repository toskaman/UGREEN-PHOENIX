You are a precise transcription clerk. A previous pass failed on one
file. Read ONLY the file named below (shown among the files) and
transcribe EVERY requirement or fact it states. Output one or more lines
with exactly 7 TAB-separated fields each, nothing else:

SUBJECT | REQUIRED_PATH | REQUIRED_CONSTRAINT | OBSERVED_PATH | OBSERVED_VALUE | SOURCE_LINES | NOTES

- SUBJECT: short name for the requirement.
- REQUIRED_PATH: the exact path demanded, or "-" if the file states a
  fact rather than demanding a path (then put the file's own path in
  OBSERVED_PATH).
- REQUIRED_CONSTRAINT: version/condition VERBATIM, or "-".
- OBSERVED_PATH: the exact path of the file you actually saw, MISSING
  if no candidate file was shown, UNREADABLE only if the input shows a
  bracketed [UNREADABLE: ...] marker for that exact path.
- OBSERVED_VALUE: relevant content VERBATIM, or "-".
- SOURCE_LINES: file path:line for every cited line.
- NOTES: OK, unless a stale marker or truncation applies.

File to transcribe (path):
