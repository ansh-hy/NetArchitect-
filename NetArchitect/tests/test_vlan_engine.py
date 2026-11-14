import pytest
from core.vlan_engine import build_vlan_plan

def test_vlan_plan_sorted():
    result = build_vlan_plan([{"vlan_id":30,"name":"STUDENTS"},{"vlan_id":10,"name":"ADMIN"}])
    assert [v.vlan_id for v in result] == [10,30]

@pytest.mark.parametrize("vlan_id", [0,4095,-1])
def test_invalid_vlan_id(vlan_id):
    with pytest.raises(ValueError): build_vlan_plan([{"vlan_id":vlan_id,"name":"BAD"}])

def test_duplicate_id_rejected():
    with pytest.raises(ValueError, match="Duplicate VLAN ID"):
        build_vlan_plan([{"vlan_id":10,"name":"ADMIN"},{"vlan_id":10,"name":"USERS"}])

def test_duplicate_name_case_insensitive():
    with pytest.raises(ValueError, match="Duplicate VLAN name"):
        build_vlan_plan([{"vlan_id":10,"name":"ADMIN"},{"vlan_id":20,"name":"admin"}])

def test_empty_name_rejected():
    with pytest.raises(ValueError): build_vlan_plan([{"vlan_id":10,"name":" "}])

def test_empty_list_allowed():
    assert build_vlan_plan([]) == []
