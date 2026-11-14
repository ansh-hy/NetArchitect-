import pytest
from core.input_validator import validate_scenario
from core.scenario_manager import load_preset
from core.project_engine import analyze_scenario

@pytest.mark.parametrize("profile", ["campus_lan", "metro_man", "global_wan"])
def test_all_presets_run_through_full_pipeline(profile):
    scenario = validate_scenario(load_preset(profile))
    result = analyze_scenario(scenario)
    assert result["subnets"]
    assert result["decision_report"]["decisions"]
    assert set(result["configurations"]) == {
        "switches.cfg", "routers.cfg", "svis.cfg", "acls.cfg",
        "vpn.cfg", "route_summarization.cfg"
    }

def test_missing_subnet_requirements_block_analysis():
    data = load_preset("campus_lan")
    data["subnet_requirements"] = []
    scenario = validate_scenario(data)
    with pytest.raises(ValueError, match="No subnet host requirements"):
        analyze_scenario(scenario)
