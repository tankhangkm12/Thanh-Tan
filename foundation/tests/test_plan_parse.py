from agentflow.plan import PlanItem, check_plan, docs_problem, parse_plan

PLAN = """# Plan

### C1 — Add greeting
- role: implementer
- files: src/greet.py, tests/test_greet.py
- done-when: `uv run pytest tests/test_greet.py`
- docs: https://docs.python.org/3/

### C2 - Tidy
- role: tester
- files: không có
- done-when: lint passes
- docs: không có — nothing to read for a rename
"""


class Roles:
    def __init__(self, *names):
        self.names = set(names)

    def roles(self):
        return self.names


def test_parse_items():
    plan = parse_plan(PLAN)
    assert [item.code for item in plan.items] == ["C1", "C2"]
    first, second = plan.items
    assert first == PlanItem(
        "C1", "Add greeting", "implementer", ("src/greet.py", "tests/test_greet.py"),
        "`uv run pytest tests/test_greet.py`", "https://docs.python.org/3/",
    )
    assert first.docs_links == ("https://docs.python.org/3/",)
    assert second.files == () and second.docs_links == ()


def test_parse_ignores_fenced_blocks_and_flags_bad_headings():
    plan = parse_plan("```\n### C9 - inside\n```\n### Notes\n### C1 - a\n- role: x\n")
    assert [item.code for item in plan.items] == ["C1"]
    assert plan.bad_headings == ("Notes",)


def test_valid_plan_has_no_problems():
    assert check_plan(parse_plan(PLAN), Roles("implementer", "tester")) == []


def test_every_problem_is_reported_with_its_code():
    text = "### C1 - a\n- role: wizard\n- docs: see the wiki\n### C1 - b\n- role: tester\n- done-when: x\n- docs: không có\n"
    problems = [str(p) for p in check_plan(parse_plan(text), Roles("tester"))]
    assert any("C1: unknown role 'wizard'" in p for p in problems)
    assert any("C1: missing 'done-when'" in p for p in problems)
    assert any("duplicate item code" in p for p in problems)
    assert any("must be a link" in p for p in problems)
    assert any("needs a reason" in p for p in problems)


def test_empty_plan_and_bad_heading_are_problems():
    assert check_plan(parse_plan("nothing here"), Roles("a"))
    assert check_plan(parse_plan("### Foo\n"), Roles("a"))


def test_files_required_when_asked():
    plan = parse_plan("### C1 - a\n- role: tester\n- done-when: x\n- docs: https://e.example/\n")
    assert check_plan(plan, Roles("tester")) == []
    assert any("files" in str(p) for p in check_plan(plan, Roles("tester"), require_files=True))


def test_rules_add_problems():
    class Never:
        def problems(self, item):
            return [f"rule hit on {item.code}"]

    plan = parse_plan(PLAN)
    problems = check_plan(plan, Roles("implementer", "tester"), rules=[Never()])
    assert [str(p) for p in problems] == ["C1: rule hit on C1", "C2: rule hit on C2"]


def test_docs_problem_variants():
    assert docs_problem("không có - lý do") is None
    assert docs_problem("") is not None
    assert docs_problem(None) is not None
