from core.input_validator import validate_scenario
from core.scenario_manager import load_preset
from core.project_engine import analyze_scenario

def test_campus_analysis_has_explanations_and_configs():
    scenario = validate_scenario(load_preset("campus_lan"))
    result = analyze_scenario(scenario)
    assert result["decision_report"]["decisions"]
    assert "switches.cfg" in result["configurations"]
    assert "routers.cfg" in result["configurations"]
    assert "svis.cfg" in result["configurations"]
    assert "acls.cfg" in result["configurations"]
    assert "vpn.cfg" in result["configurations"]
    assert "route_summarization.cfg" in result["configurations"]
    assert "router ospf" in result["configurations"]["svis.cfg"].lower()

def test_generated_svis_use_allocated_gateway():
    scenario = validate_scenario(load_preset("campus_lan"))
    result = analyze_scenario(scenario)
    svis = result["configurations"]["svis.cfg"]
    for subnet in result["subnets"]:
        if any(v.name.lower() == subnet.name.lower() for v in result["vlans"]):
            assert subnet.gateway in svis

def test_explainability_contains_vlsm_math():
    scenario = validate_scenario(load_preset("campus_lan"))
    result = analyze_scenario(scenario)
    vlsm_decisions = [d for d in result["decision_report"]["decisions"] if d["area"].startswith("VLSM")]
    assert vlsm_decisions
    assert "usable addresses" in vlsm_decisions[0]["rationale"]


def test_decision_report_includes_rfc_and_subnet_math():
    scenario = validate_scenario(load_preset("campus_lan"))
    result = analyze_scenario(scenario)
    decisions = result["decision_report"]["decisions"]
    routing = next(d for d in decisions if d["area"] == "Routing")
    assert "RFC 2328" in routing["reference"]
    subnet = next(d for d in decisions if d["area"].startswith("VLSM"))
    assert "2^" in subnet["rationale"]
    assert "utilization" in subnet["rationale"]
    media = next(d for d in decisions if d["area"] == "Physical media")
    assert "850 nm" in media["transceiver_rationale"]
