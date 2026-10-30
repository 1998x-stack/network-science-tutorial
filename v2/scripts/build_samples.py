"""Generate self-contained browser demos from the exact same Python model implementation."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from netsci.experiment import build_artifact
from netsci.models import erdos_renyi, watts_strogatz, barabasi_albert

samples = {
    "er": build_artifact(erdos_renyi(80, 6 / 79, 42), model="er", params={"n": 80, "p": 6 / 79}, seed=42),
    "ws": build_artifact(watts_strogatz(80, 6, .08, 42), model="ws", params={"n": 80, "k": 6, "p": .08}, seed=42),
    "ba": build_artifact(barabasi_albert(80, 3, 42), model="ba", params={"n": 80, "m": 3}, seed=42),
}
output = ROOT / "apps" / "graph-lab" / "samples.js"
output.write_text("window.NETSCI_SAMPLES = " + json.dumps(samples, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
print(output)
