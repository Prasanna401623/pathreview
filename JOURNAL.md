# PathReview — Module 3 Journal

## Week 7 — Issue selection

**Issue link:** https://github.com/ascherj/pathreview/issues/154

**Issue title:** Health check DB probe passes a raw SQL string, which fails under SQLAlchemy 2.x

**Tier:** [x] Tier 1  [ ] Tier 2  [ ] Tier 3

**Problem summary:**
The `/health` endpoint checks that PostgreSQL is reachable by running
`await db.execute("SELECT 1")`, passing the query as a plain Python string.
SQLAlchemy 2.x no longer accepts raw string SQL in `execute()` — the statement
must be wrapped in `sqlalchemy.text()` — so this call raises an error and the
Postgres probe is reported as `unhealthy` even when the database is perfectly
fine. Because any unhealthy dependency flips the overall status, the endpoint
then returns HTTP 503, which can falsely trip uptime monitors and deployment
health gates. A successful fix wraps the query in `text()` (and imports it) so
the probe executes correctly and reports the true database status. The change
is isolated to `api/routes/health.py`, backed by a unit test asserting the
endpoint returns 200 when the database is up.

**Branch name:** fix/154-health-check-db-probe

**Setup confirmation:** [x] App runs locally at localhost:5173

**Cohort ledger:** [x] Issue added to cohort ledger

### Selection notes — "Is this right for me?" checklist

- **Scope is small and well-bounded.** The defect and its fix live in a single
  file (`api/routes/health.py`, line 31). I confirmed this by reading the file
  directly rather than trusting the title.
- **I understand the root cause.** SQLAlchemy 2.x removed implicit autocommit
  and "plain string" execution; textual SQL must go through `text()`. This is a
  well-documented, canonical migration issue, not an obscure edge case.
- **The fix is verifiable.** I can prove the fix with a focused unit test on the
  health endpoint (expect 200 + `postgres: "healthy"` when the DB is up), which
  fits the project's "every change includes a test" standard.
- **No hidden dependencies.** The fix doesn't touch the LLM/RAG/agent pipeline,
  so it doesn't require an OpenRouter API key or model access to validate.
- **Right difficulty for a first contribution.** Labeled `good first issue` /
  `tier-1`, estimated at 1–2 hours, and it teaches a real, transferable lesson
  about the SQLAlchemy 1.x → 2.x API change.

**Conclusion:** Good fit — clear cause, single-file change, easily tested, and
independent of external services.
