import pytest
from core.media_engine import select_media, validate_copper_request, PhysicalDistanceViolationError
from core.routing_engine import select_routing
from core.vlan_engine import build_vlan_plan
from core.vlsm_engine import allocate_vlsm, AddressSpaceExhaustedError

@pytest.mark.parametrize("distance,expected", [
    (100, "Cat6a Copper"),
    (100.0001, "OM4 Multimode Fiber"),
    (400, "OM4 Multimode Fiber"),
    (400.0001, "OS2 Single-Mode Fiber"),
])
def test_assignment_media_thresholds(distance, expected):
    assert select_media(distance).media == expected

def test_copper_boundary_error_is_strictly_over_100m():
    assert validate_copper_request(100) is None
    with pytest.raises(PhysicalDistanceViolationError):
        validate_copper_request(100.0001)

def test_vlan_upper_valid_boundary():
    assert build_vlan_plan([{"vlan_id":4094,"name":"LAST"}])[0].vlan_id == 4094

def test_vlan_zero_rejected():
    with pytest.raises(ValueError):
        build_vlan_plan([{"vlan_id":0,"name":"BAD"}])

def test_ospf_threshold_exactly_49_and_50():
    assert select_routing(49).protocol == "OSPF Area 0"
    assert select_routing(50).protocol == "Routing design review required"

def test_vlsm_exact_capacity_and_one_more_exhausts():
    # A /29 has six conventional usable IPv4 host addresses.
    allocated = allocate_vlsm("192.0.2.0/29", [{"name":"six","hosts":6}])
    assert allocated[0].network == "192.0.2.0/29"
    with pytest.raises(AddressSpaceExhaustedError):
        allocate_vlsm("192.0.2.0/29", [{"name":"six","hosts":6},{"name":"one","hosts":1}])


def test_very_long_os2_span_flags_transport_regeneration():
    result = select_media(1_000_000)
    assert result.media == "OS2 Single-Mode Fiber"
    assert "transport" in result.transceiver.lower()
    assert "regeneration" in result.rationale.lower()
