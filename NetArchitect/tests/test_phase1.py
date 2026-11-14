import pytest
from core.scenario_manager import load_preset, list_presets
from core.input_validator import validate_scenario


@pytest.mark.parametrize("name", list_presets())
def test_presets_load_and_validate(name):
    scenario = validate_scenario(load_preset(name))
    assert scenario.name
    assert scenario.endpoints > 0
    assert scenario.root_network.version == 4


def test_unknown_preset_rejected():
    with pytest.raises(ValueError):
        load_preset("not_a_profile")


def test_invalid_negative_distance_rejected():
    data = load_preset("campus_lan")
    data["max_link_distance_m"] = -1
    with pytest.raises(Exception):
        validate_scenario(data)


def test_ipv6_root_network_rejected():
    data = load_preset("campus_lan")
    data["root_network"] = "2001:db8::/32"
    with pytest.raises(Exception):
        validate_scenario(data)
