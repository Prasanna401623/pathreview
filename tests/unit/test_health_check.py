"""Reproduction test for issue #154.

https://github.com/ascherj/pathreview/issues/154

The health check in ``api/routes/health.py`` verifies PostgreSQL by running
``await db.execute("SELECT 1")`` -- passing the query as a plain Python string.
SQLAlchemy 2.x refuses to execute a bare string; textual SQL must be wrapped in
``sqlalchemy.text()``. Because of this, the Postgres probe raises, the health
check reports the database as "unhealthy", and ``GET /health`` returns HTTP 503
even when the database is actually up.

These tests reproduce that root cause with an in-memory SQLite engine (the same
SQLAlchemy library the app uses, so no external database is required) and pin
down the fix that Week 9 will apply to ``health.py``.
"""

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.exc import ObjectNotExecutableError


def test_raw_string_select_is_rejected_by_sqlalchemy_2x() -> None:
    """Issue #154: this is exactly what health.py does today, and it fails.

    ``db.execute("SELECT 1")`` raises ``ObjectNotExecutableError`` under
    SQLAlchemy 2.x, which is why the Postgres health probe wrongly reports the
    database as unhealthy.
    """
    engine = create_engine("sqlite://")
    with engine.connect() as conn, pytest.raises(ObjectNotExecutableError):
        conn.execute("SELECT 1")


def test_text_wrapped_select_executes_correctly() -> None:
    """The Week 9 fix: wrapping the query in ``text()`` executes correctly."""
    engine = create_engine("sqlite://")
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        assert result.scalar() == 1
