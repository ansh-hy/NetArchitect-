import math
import pytest
from core.media_engine import select_media, validate_copper_request
from core.input_validator import validate_scenario
from core.scenario_manager import load_preset
from core.project_engine import analyze_scenario

@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
def test_non_finite_media_distance_rejected(value):
    with pytest.raises(ValueError, match="finite"):
        select_media(value)

@pytest.mark.parametrize("value", [float("nan"), float("inf")])
def test_non_finite_copper_distance_rejected(value):
    with pytest.raises(ValueError, match="finite"):
        validate_copper_request(value)

def test_campus_ospf_is_on_layer3_gateway_switch():
    scenario = validate_scenario(load_preset("campus_lan"))
    result = analyze_scenario(scenario)
    assert "router ospf 1" in result["configurations"]["svis.cfg"].lower()
    assert "network 10." in result["configurations"]["svis.cfg"].lower()
    assert "router ospf 1" not in result["configurations"]["routers.cfg"].lower()

def test_multi_area_configuration_is_not_falsely_claimed_as_area0():
    scenario = validate_scenario(load_preset("metro_man"))
    result = analyze_scenario(scenario)
    svis = result["configurations"]["svis.cfg"].lower()
    assert "subnet-to-area mapping" in svis
    assert "router ospf 1" not in svis

def test_acl_does_not_emit_unapproved_permit_any():
    scenario = validate_scenario(load_preset("campus_lan"))
    result = analyze_scenario(scenario)
    acl = result["configurations"]["acls.cfg"].lower()
    assert "permit ip" not in acl
    assert "policy" in acl
