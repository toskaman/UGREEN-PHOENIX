# Open platform questions for UGREEN support (PHOENIX)

Context: `phoenix-recovery-intelligence`, a document-level recovery-readiness
Skill delegating to `file-agent`, `document-agent`, and `knowledge-agent`
(`uliya-skill-kit` 0.7.3, capability catalog 2.0.0, checker `static-pass`).
No NAS access yet; these answers will finalize the Skill before the finalist
test day.

## Authorized scope

1. How is the user-authorized NAS scope expressed to experts (exact path
   syntax, trailing-slash rules)? Are multi-folder scopes and symlinks
   supported, and how are scope violations reported?

## file-agent (`ug-filesystem`: find, ls, stat, sha256sum)

2. What are the `find` limits (max results, max depth, timeout), and how is
   a truncated search signaled vs. a genuine no-result?
3. How are "not found", "access denied", and "timeout" distinguished in
   expert results (exact status fields or codes to branch on)?

## document-agent (`ug-document`: qa, extract, reconcile)

4. Which document formats are supported (PDF, DOCX, plain text, images)?
   What is the max document size per call, and how is truncation signaled?
5. What are the input limits for `reconcile` (number/size of documents per
   call)?

## knowledge-agent (`ug-knowledge`: collect-evidence, save-text)

6. What are the `collect-evidence` batch/context limits?
7. For `save-text`: approval granularity (per call, per file, per session)? 
   Output path rules, overwrite behavior, and the exact success result
   (verified output path field)?

## Approvals and delegation

8. Which actions require workflow approval, how is approval requested and
   surfaced to the user, and what state follows a denial (partial result
   preserved or full cancel)?
9. Confirm the exact `delegate --target ...` CLI syntax and how upstream
   results are passed (size limits?), plus the exact completion vocabulary
   (`completed` / `failed` / `cancelled` / `waiting_*`).

## Finalist test environment

10. How is the 24-hour remote NAS session provided (access method, skill
    install procedure, observable logs)? Can the Skill be iterated during
    the session, and will the device run exactly kit 0.7.3 / catalog 2.0.0?
11. Where do the models run (on-device NPU, local, cloud)? Which input
    languages are supported (e.g., French prompts)?
