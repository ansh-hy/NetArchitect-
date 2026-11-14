import ipaddress
import pytest
from core.vlsm_engine import (
    allocate_vlsm, prefix_for_hosts, wildcard_from_prefix,
    AddressSpaceExhaustedError
)

@pytest.mark.parametrize("hosts,prefix", [(500,23),(250,24),(100,25),(50,26),(20,27),(1,30),(2,30)])
def test_prefix_for_hosts(hosts, prefix):
    assert prefix_for_hosts(hosts) == prefix

@pytest.mark.parametrize("prefix,wildcard", [
    (0,"255.255.255.255"), (23,"0.0.1.255"), (24,"0.0.0.255"),
    (25,"0.0.0.127"), (26,"0.0.0.63"), (30,"0.0.0.3"),
    (31,"0.0.0.1"), (32,"0.0.0.0")
])
def test_wildcard(prefix, wildcard):
    assert wildcard_from_prefix(prefix) == wildcard

def test_vlsm_descending_non_overlapping_and_inside_root():
    result = allocate_vlsm("192.168.0.0/16", [
        {"name":"Small","hosts":20}, {"name":"Large","hosts":500},
        {"name":"Medium","hosts":100}
    ])
    assert result[0].name == "Large"
    nets = [ipaddress.ip_network(s.network) for s in result]
    root = ipaddress.ip_network("192.168.0.0/16")
    assert all(n.subnet_of(root) for n in nets)
    assert all(not nets[i].overlaps(nets[j]) for i in range(len(nets)) for j in range(i+1,len(nets)))

def test_gateway_is_first_usable():
    result = allocate_vlsm("10.0.0.0/24", [{"name":"Users","hosts":50}])[0]
    assert result.gateway == result.first_usable
    assert result.gateway == "10.0.0.1"

def test_address_space_exhaustion():
    with pytest.raises(AddressSpaceExhaustedError):
        allocate_vlsm("192.0.2.0/30", [{"name":"TooMany","hosts":10}])

def test_duplicate_subnet_name_rejected():
    with pytest.raises(ValueError, match="Duplicate subnet name"):
        allocate_vlsm("10.0.0.0/24", [{"name":"Users","hosts":10},{"name":"users","hosts":10}])

def test_noncanonical_root_rejected():
    with pytest.raises(ValueError):
        allocate_vlsm("10.0.0.1/24", [{"name":"Users","hosts":10}])

def test_invalid_hosts_rejected():
    with pytest.raises(ValueError):
        prefix_for_hosts(0)
