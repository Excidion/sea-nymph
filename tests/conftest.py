import shutil
from pathlib import Path

import pytest

DOCS_TESTS_DIR = Path("docs/tests")


def _module_path(fspath: Path) -> Path:
    stem = fspath.stem.removeprefix("test_")
    if stem == "figure":
        return Path("mermaidplotlib")
    return Path("sea_nymph") / stem


@pytest.fixture(scope="session", autouse=True)
def clean_docs_tests():
    index = DOCS_TESTS_DIR / "index.md"
    saved = index.read_text(encoding="utf-8") if index.exists() else None
    if DOCS_TESTS_DIR.exists():
        shutil.rmtree(DOCS_TESTS_DIR)
    DOCS_TESTS_DIR.mkdir(parents=True, exist_ok=True)
    if saved is not None:
        index.write_text(saved, encoding="utf-8")


@pytest.fixture(autouse=True)
def per_test_figure_saver(request):
    if request.cls is None:
        yield
        return
    request.cls._figures = []
    yield
    figures = request.cls._figures
    if figures:
        class_dir = (
            DOCS_TESTS_DIR / _module_path(Path(request.fspath)) / request.cls.__name__
        )
        class_dir.mkdir(parents=True, exist_ok=True)
        path = class_dir / f"{request.node.name}.md"
        path.write_text("\n\n".join(str(f) for f in figures) + "\n", encoding="utf-8")
