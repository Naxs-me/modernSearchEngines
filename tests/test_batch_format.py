from pathlib import Path

def test_queries_file_format():
    path = Path("data/queries.tsv")
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                assert "\t" in line
