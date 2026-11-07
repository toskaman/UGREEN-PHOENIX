# Wave-1 support request (send-ready)

To: UGREEN hackathon support (via the channel announced for finalists)
Subject: PHOENIX finalist — 11 platform questions before the NAS test day

---

Hello,

My project PHOENIX (`phoenix-recovery-intelligence`, a document-level
recovery-readiness Skill) was selected as a finalist. The package passes
the official static checker with zero errors and zero warnings
(`uliya-skill-kit` 0.7.3, capability catalog 2.0.0), and my eight test
corpora plus an hour-by-hour runbook are ready for the NAS session.

To use the 24-hour session for execution rather than discovery, could you
please confirm the following?

**Authorized scope**
1. How is the user-authorized NAS scope expressed to experts (exact path
   syntax)? Are multi-folder scopes and symlinks supported, and how are
   scope violations reported?

**file-agent (`ug-filesystem`)**
2. What are the `find` limits (max results, depth, timeout), and how is a
   truncated search signaled versus a genuine no-result?
3. How are "not found", "access denied", and "timeout" distinguished in
   expert results (exact status fields or codes)?

**document-agent (`ug-document`)**
4. Which document formats are supported, what is the max size per call, and
   how is truncation signaled?
5. What are the `reconcile` input limits (documents per call)?

**knowledge-agent (`ug-knowledge`)**
6. What are the `collect-evidence` batch and context limits?
7. For `save-text`: approval granularity, output path rules, overwrite
   behavior, and the exact success fields?

**Approvals and delegation**
8. Which actions require workflow approval, how is approval surfaced, and
   what state follows a denial?
9. Please confirm the exact `delegate --target ...` syntax, how upstream
   results are passed (size limits?), and the exact completion vocabulary.

**Test environment**
10. How is the 24-hour session provided (access, install, logs)? Can the
    Skill be iterated during the session, and will the device run exactly
    kit 0.7.3 / catalog 2.0.0?
11. Which model runs the Skill (on-device, cloud, or both), and which input
    languages are supported?

Thank you for the hackathon and for any answers you can share before the
session.

[Your name]
[Devpost project URL]
[GitHub: https://github.com/toskaman/UGREEN-PHOENIX]
