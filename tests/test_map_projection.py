import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.skipif(shutil.which("node") is None, reason="node no disponible")
def test_map_projection_matches_d3_fixtures():
    result = subprocess.run(
        ["node", "scripts/check_map_projection.mjs"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "5 puntos" in result.stdout
