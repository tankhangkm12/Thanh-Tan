"""The templates, checklists and profiles.md of design-architecture, and the sample draft built from them, stay in line with the scripts.

Run with: uv run --with pytest --with pyyaml pytest families/design-system/core/scripts
"""

import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import check_profile as cp  # noqa: E402
import idlist  # noqa: E402

ARCH = HERE.parent.parent / "design-architecture"
TEMPLATES = ARCH / "templates"
CHECKLISTS = ARCH / "checklists"
SAMPLE = ARCH / "examples" / "cafe-order"
STAGES = (HERE.parent / "workflow" / "stages.md").read_text(encoding="utf-8")
IDS = idlist.load()
TODAY = "2026-10-13"  # the sample's end-of-support dates are checked against a fixed day, not the day the test runs

TEMPLATE_FILES = sorted(p for p in TEMPLATES.rglob("*.md"))
RELS = [p.relative_to(TEMPLATES).as_posix() for p in TEMPLATE_FILES]
# Written by calc_capacity.py: the template only describes the file, so it has no `<!-- required -->` section.
GENERATED = {"00-context/assumptions.md", "03-capacity/workload-model.md", "03-capacity/data-sizing.md", "03-capacity/storage-sizing.md",
             "03-capacity/compute-sizing.md", "03-capacity/cost-model.md"}
# The parts that have templates in Phase 4, and the checklist file for each.
CHECKLISTS_OF = {"00-context": "00-context.md", "02-tech-stack": "02-tech-stack.md", "03-capacity": "03-capacity.md", "04-flows": "04-flows.md",
                 "06-backend": "06-backend.md", "07-data": "07-data.md"}


def lines_of(path: Path) -> list[str]:
    return cp.read_lines(path)


# --- the templates ------------------------------------------------------------------------------------------------------------

def test_there_are_templates():
    assert TEMPLATE_FILES, "design-architecture/templates is empty"
    assert {rel.split("/")[0] for rel in RELS} == set(CHECKLISTS_OF)


@pytest.mark.parametrize("rel", RELS)
def test_template_path_has_no_angle_brackets(rel):
    assert "<" not in rel and ">" not in rel, "< and > cannot be used in a file name on Windows: use {name} or xxx"


@pytest.mark.parametrize("rel", RELS)
def test_template_has_a_required_section_unless_a_script_writes_the_file(rel):
    required = cp.required_headings(lines_of(TEMPLATES / rel))
    if rel in GENERATED:
        assert required == [], "a file written by calc_capacity.py has nothing the Designer must fill"
    else:
        assert required, "a template that the Designer fills needs at least one <!-- required --> section"


@pytest.mark.parametrize("rel", RELS)
def test_required_mark_comes_straight_after_a_heading_and_every_mark_counts(rel):
    lines = lines_of(TEMPLATES / rel)
    masked = cp.mask_fences(lines)
    marks = [i for i, line in enumerate(masked) if cp.REQUIRED_MARK.fullmatch(line.strip())]  # a note may quote the mark inside backticks
    for i in marks:
        assert i > 0 and cp.HEADING_RE.match(masked[i - 1]), f"{rel}:{i + 1} the mark must be on the line right after a heading"
    assert len(marks) == len(cp.required_headings(lines)), "a stray mark that required_headings does not read"


@pytest.mark.parametrize("rel", RELS)
def test_template_names_no_real_id(rel):
    """A real ID in a template would become a second definition of that ID in every draft made from it."""
    text = "\n".join(lines_of(TEMPLATES / rel))
    real = sorted({m.group(1) for m in IDS.id_re().finditer(text) if not IDS.is_placeholder(m.group(1))})
    assert real == []


def test_project_profile_template_has_a_level_and_all_thirteen_parts():
    path = TEMPLATES / "00-context" / "project-profile.md"
    rows, findings = cp.parse_profile(path, "00-context/project-profile.md")
    assert [f.render() for f in findings] == []
    assert list(rows) == list(cp.PARTS)


def test_tables_template_has_exactly_one_pending_calc_pair_and_no_marker_text_elsewhere():
    import calc_capacity as cc

    text = (TEMPLATES / "07-data" / "databases" / "{db}" / "tables.md").read_text(encoding="utf-8")
    pairs = list(cc.CALC_BLOCK.finditer(text))
    assert len(pairs) == 1 and pairs[0].group(3).strip() == cc.PENDING
    assert text.count("<!-- BEGIN:calc") == 1 and text.count("<!-- END:calc") == 1  # the note at the top must not quote a whole marker


def test_a_template_with_a_placeholder_folder_matches_an_object_folder():
    assert cp.match_template("06-backend/services/order-service/scaling.md", RELS) == "06-backend/services/{service}/scaling.md"
    assert cp.match_template("07-data/databases/order-db/tables.md", RELS) == "07-data/databases/{db}/tables.md"
    assert cp.match_template("04-flows/FL-001-dat-don.md", RELS) == "04-flows/FL-xxx-{tên}.md"
    assert cp.match_template("02-tech-stack/layers/data.md", RELS) == "02-tech-stack/layers/{layer}.md"


# --- the checklists and profiles.md --------------------------------------------------------------------------------------------

def test_every_templated_part_has_a_checklist_and_there_is_no_other():
    assert sorted(p.name for p in CHECKLISTS.glob("*.md")) == sorted(CHECKLISTS_OF.values())
    for name in CHECKLISTS_OF.values():
        assert re.search(r"^- \[ \] ", (CHECKLISTS / name).read_text(encoding="utf-8"), re.MULTILINE)


def table_rows(text: str, first_header: str) -> list[list[str]]:
    rows, inside = [], False
    for line in text.splitlines():
        if not line.lstrip().startswith("|"):
            inside = False
            continue
        cells = cp.split_cells(line)
        if cp.heading_key(cells[0]) == first_header.casefold():
            inside = True
            continue
        if inside and not re.fullmatch(r"[:\-\s|]*", line):
            rows.append(cells)
    return rows


def stages_level_values() -> dict[str, list[str]]:
    """{part: [S, M, L, XL]} from the table "Phần của architecture/ theo mức áp dụng" of stages.md."""
    def value(cell: str) -> str:
        cell = cp.heading_key(cell)
        return "có" if cell.startswith(("có", "thêm")) else "bỏ" if cell.startswith("bỏ") else "rút gọn"

    section = STAGES.split("## Phần của `architecture/` theo mức áp dụng", 1)[1].split("\n## ", 1)[0]
    out: dict[str, list[str]] = {}
    for cells in table_rows(section, "Phần"):
        for part in re.findall(r"\d\d-[a-z-]+", cells[0]):
            out[part] = [value(c) for c in cells[1:5]]
    return out


def test_profiles_md_part_table_equals_the_table_of_stages_md():
    text = (ARCH / "profiles.md").read_text(encoding="utf-8")
    section = text.split("## Dòng cấp phần", 1)[1].split("\n## ", 1)[0]
    ours = {cells[0]: [cp.heading_key(c) for c in cells[1:5]] for cells in table_rows(section, "Phần")}
    assert list(ours) == list(cp.PARTS)
    assert ours == stages_level_values()
    assert all(v in cp.VALUES for values in ours.values() for v in values)


def test_profiles_md_file_rows_name_files_of_a_part_that_is_cut_down_at_level_s():
    text = (ARCH / "profiles.md").read_text(encoding="utf-8")
    section = text.split("## Dòng cấp file", 1)[1].split("\n## ", 1)[0]
    rows = table_rows(section, "File")
    assert rows
    for cells in rows:
        part = cells[0].split("/")[0]
        assert part in cp.PARTS and stages_level_values()[part][0] == "rút gọn", cells[0]
        assert cells[2:5] == ["có", "có", "có"]


# --- the sample draft ----------------------------------------------------------------------------------------------------------

@pytest.fixture()
def sample(tmp_path):
    workspace = tmp_path / "cafe-order"
    shutil.copytree(SAMPLE, workspace)
    return workspace


def run(script: str, workspace: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-X", "utf8", str(HERE / script), "--workspace", str(workspace), *args, "--date", TODAY],
                          capture_output=True, text=True, encoding="utf-8")


def test_the_sample_has_no_check_reports_and_no_generated_file_is_stale(sample):
    assert not (SAMPLE / "checks").exists()
    result = run("calc_capacity.py", sample, "--check")
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize("script,args", [
    ("check_profile.py", ("--gate", "G6", "--templates", str(TEMPLATES))),
    ("check_trace.py", ("--gate", "G7")),
    ("check_links.py", ()),
    ("check_versions.py", ()),
])
def test_scripts_run_clean_on_the_sample(sample, script, args):
    result = run(script, sample, *args)
    assert result.returncode == 0, result.stdout + result.stderr


def test_the_sample_does_not_pass_gate_g7_for_the_parts_it_does_not_have(sample):
    """The sample stops at the Phase 4 parts, so G7 wants 05-frontend. Phase 5 widens the sample to all 13 parts."""
    result = run("check_profile.py", sample, "--gate", "G7", "--templates", str(TEMPLATES))
    assert result.returncode == 1 and "05-frontend" in result.stdout + result.stderr
