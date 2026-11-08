# PHOENIX demo video script (3 minutes, finalist stage)

Record only on the real NAS during the 24-hour session. All footage below
assumes the wave-1 runs from `wave1/run-log.md` are already captured.

## Narration (timed, ~230 words, ~90s speech + screen time)

**0:00–0:25 — Problem.** [SCREEN: NAS file browser full of project files]
"Small teams keep everything on their NAS — code, guides, configs. But after
a lost laptop or a departure, one question matters: do these files actually
let us resume work? Search finds files. Backup dashboards show backup status.
Neither answers that question."

**0:25–1:05 — Live run 1: the missing config.** [SCREEN: paste W1-A, report
appears; highlight the blocker row and citation]
"PHOENIX investigates. Here it finds the deployment guide requires a
production config that is absent from the authorized folder — even though a
stale copy with the same name sits elsewhere. Filename search is fooled;
PHOENIX is not, because a filename match alone is never enough evidence.
Every claim carries its exact source."

**1:05–1:40 — Live run 2: the version conflict.** [SCREEN: paste W1-B;
highlight both cited versions]
"Second case: the config exists, but declares version 2.4.1 where the guide
requires 3.0 or newer. PHOENIX flags the conflict and cites both sources
side by side — instead of silently picking one."

**1:40–2:25 — Fix, recheck, Recovery Delta.** [SCREEN: operator adds the
missing config; paste prior report + recheck; Delta section appears]
"Now the part no search box does. We fix the cited problem — then PHOENIX
re-inspects the folder from scratch. It never takes our word for it. The
Recovery Delta shows the before and after evidence side by side: this
blocker resolved, that uncertainty still open. Diagnosis, correction,
proof — in one loop."

**2:25–2:45 — Honesty.** [SCREEN: edge-case verdict INSUFFICIENT EVIDENCE]
"And when evidence is incomplete or unreadable, PHOENIX abstains. It reports
documentary readiness — never a tested recovery. That distinction is the
whole point."

**2:45–3:00 — Closing.** [SCREEN: report list + repo URL]
"PHOENIX: recovery intelligence for UGREEN AI NAS. Evidence first, claims
cited, limits stated."

## Recording checklist

- [ ] 1080p screen capture of the real NAS session (no mockups; raw footage kept)
- [ ] Narration recorded separately in a quiet room if live audio is risky
- [ ] On-screen text minimal: verdicts and citations must be readable
- [ ] Disclaimer shown or spoken: "Demonstration on UGREEN AI NAS; documentary
      readiness assessment, not a verified system restore."
- [ ] Final cut under the published length limit; export + backup before the
      session ends
