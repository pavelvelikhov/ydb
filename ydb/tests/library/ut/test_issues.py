import copy

import pytest

from ydb.tests.library.common.issues import issues_without_rbo_fallback, text_without_rbo_fallback


FALLBACK = {"severity": 3, "message": "Compilation with the new RBO failed: unsupported query"}


@pytest.mark.parametrize("issue", [
    {**FALLBACK, "severity": 1},
    {**FALLBACK, "severity": 2},
    {**FALLBACK, "issue_code": 42},
    {"severity": 3, "message": "Another informational diagnostic"},
])
def test_keep_other_issues(issue):
    assert issues_without_rbo_fallback([FALLBACK, issue]) == [issue]


def test_nested_fallback_preserves_real_errors_and_input():
    error = {"severity": 1, "issue_code": 2028, "message": "Table schema changed"}
    wrapper = {"severity": 3, "issue_code": 1060, "message": "Execution", "issues": [FALLBACK, error]}
    original = copy.deepcopy(wrapper)
    assert issues_without_rbo_fallback([wrapper]) == [{**wrapper, "issues": [error]}]
    assert wrapper == original
    assert issues_without_rbo_fallback([{**wrapper, "issues": [FALLBACK]}]) == []
    # An error wrapper must remain, even if its only child was the fallback note.
    assert issues_without_rbo_fallback([{**wrapper, "severity": 1, "issues": [FALLBACK]}]) == [
        {**wrapper, "severity": 1, "issues": []}
    ]


def test_text_filter_preserves_error_warning_and_unrelated_info():
    preserved = (
        "<main>: Error: Compilation with the new RBO failed: user error\n"
        "<main>: Warning: Compilation with the new RBO failed: warning\n"
        "<main>: Info: Another informational diagnostic\n"
        "    <main>:3:17: Error: Invalid argument, code: 2031\n"
    )
    assert text_without_rbo_fallback(
        "<main>: Info: Compilation with the new RBO failed: [ { Error: internal reason } ]\n" + preserved
    ) == preserved
