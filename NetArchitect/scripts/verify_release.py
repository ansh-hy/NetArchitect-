"""Release gate: run all preset engines and verify generated artifact invariants."""
from pathlib import Path
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.input_validator import validate_scenario
from core.scenario_manager import load_preset
from core.project_engine import analyze_scenario

REQUIRED_CONFIGS = {"switches.cfg", "routers.cfg", "svis.cfg", "acls.cfg", "vpn.cfg", "route_summarization.cfg"}
profiles = ("campus_lan", "metro_man", "global_wan")

for profile in profiles:
    scenario = validate_scenario(load_preset(profile))
    result = analyze_scenario(scenario)
    assert result["subnets"], f"{profile}: no subnet allocations"
    assert result["decision_report"]["decisions"], f"{profile}: no decision rationale"
    assert set(result["configurations"]) == REQUIRED_CONFIGS
    assert all(result["configurations"][name].strip().endswith("end") for name in REQUIRED_CONFIGS)
    out = ROOT / "exports" / profile
    assert out.exists(), f"{profile}: export directory missing"
    for filename in REQUIRED_CONFIGS:
        assert (out / filename).exists(), f"{profile}: {filename} missing"
    for filename in ("decision_report.json", "vlsm_allocations.json", "vlsm_allocations.csv", "SIMULATION_REQUIRED.txt"):
        assert (out / filename).exists(), f"{profile}: {filename} missing"
    if profile == "campus_lan":
        assert "router ospf 1" in result["configurations"]["svis.cfg"].lower()
        assert "router ospf 1" not in result["configurations"]["routers.cfg"].lower()
        assert "permit ip" not in result["configurations"]["acls.cfg"].lower()
    if profile == "global_wan":
        assert "peer public ip" in result["configurations"]["vpn.cfg"].lower()
        assert "site-to-prefix" in result["configurations"]["route_summarization.cfg"].lower()
    if profile in ("metro_man", "global_wan"):
        assert "subnet-to-area mapping" in result["configurations"]["svis.cfg"].lower() or result["routing"].protocol == "eBGP"
    print(f"PASS: {profile} analysis and artifact invariants")

print("PASS: all three presets")
