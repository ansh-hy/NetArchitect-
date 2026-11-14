import pytest
from core.topology_engine import recommend_topology
from core.redundancy_engine import recommend_redundancy

@pytest.mark.parametrize("profile,expected", [
("campus_lan","Hierarchical campus LAN (core/distribution/access)"),
("metro_man","Metro Ethernet hub-and-spoke with dual-homed site connectivity"),
("global_wan","Distributed enterprise WAN with cloud connectivity")])
def test_topology_profiles(profile, expected):
    result = recommend_topology(profile,3,3,True)
    assert result.topology == expected
    assert result.rationale

def test_invalid_topology_counts():
    with pytest.raises(ValueError): recommend_topology("campus_lan",0,3,False)

def test_metro_redundancy():
    result = recommend_redundancy(True,"metro_man",3)
    assert result["enabled"] and "Dual-homed" in result["design"]

def test_redundancy_disabled():
    assert not recommend_redundancy(False,"campus_lan",1)["enabled"]
