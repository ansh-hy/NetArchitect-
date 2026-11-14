import pytest
from core.routing_engine import select_routing

def test_single_as_under_50_selects_area0():
    result = select_routing(49)
    assert result.protocol == "OSPF Area 0"

def test_multi_site_selects_multi_area_policy():
    result = select_routing(20, multi_site=True)
    assert result.protocol.startswith("Multi-Area OSPF")

def test_external_as_selects_ebgp():
    result = select_routing(20, cloud_boundary=True, external_as_boundary=True)
    assert result.protocol == "eBGP"

def test_50_subnet_undefined_case_is_flagged():
    result = select_routing(50)
    assert result.protocol == "Routing design review required"

def test_invalid_subnet_count():
    with pytest.raises(ValueError):
        select_routing(0)
