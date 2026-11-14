"""Deterministic IPv4 VLSM allocation with containment and overlap checks."""
from __future__ import annotations
import ipaddress
import math
from dataclasses import dataclass


class AddressSpaceExhaustedError(ValueError):
    """Raised when the requested subnets cannot fit in the root prefix."""


@dataclass(frozen=True)
class SubnetAllocation:
    name: str
    requested_hosts: int
    network: str
    prefix: int
    subnet_mask: str
    wildcard_mask: str
    network_address: str
    first_usable: str
    gateway: str
    last_usable: str
    broadcast_address: str
    total_addresses: int
    usable_addresses: int
    utilization_percent: float


def prefix_for_hosts(hosts: int) -> int:
    """Return conventional IPv4 LAN prefix; reserves network and broadcast."""
    if isinstance(hosts, bool) or not isinstance(hosts, int):
        raise TypeError("Host requirement must be an integer.")
    if hosts <= 0:
        raise ValueError("Host requirement must be greater than zero.")
    host_bits = math.ceil(math.log2(hosts + 2))
    if host_bits > 30:
        raise ValueError("Host requirement is too large for a conventional IPv4 LAN subnet.")
    return 32 - host_bits


def wildcard_from_prefix(prefix: int) -> str:
    if isinstance(prefix, bool) or not isinstance(prefix, int) or not 0 <= prefix <= 32:
        raise ValueError("IPv4 prefix must be an integer from 0 to 32.")
    mask = int(ipaddress.IPv4Network(f"0.0.0.0/{prefix}").netmask)
    return str(ipaddress.IPv4Address(0xFFFFFFFF ^ mask))


def allocate_vlsm(root_network: str, requirements: list[dict]) -> list[SubnetAllocation]:
    try:
        root = ipaddress.ip_network(root_network, strict=True)
    except ValueError as exc:
        raise ValueError(f"Invalid or non-canonical root network: {exc}") from exc
    if root.version != 4:
        raise ValueError("Only IPv4 VLSM allocation is supported.")
    if not isinstance(requirements, list) or not requirements:
        raise ValueError("At least one subnet host requirement is required.")

    normalized = []
    seen_names = set()
    for item in requirements:
        if not isinstance(item, dict):
            raise ValueError("Each subnet requirement must be an object.")
        name = item.get("name")
        hosts = item.get("hosts")
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Every subnet must have a non-empty name.")
        if name.strip().lower() in seen_names:
            raise ValueError(f"Duplicate subnet name: {name}.")
        seen_names.add(name.strip().lower())
        prefix = prefix_for_hosts(hosts)
        if prefix < root.prefixlen:
            raise AddressSpaceExhaustedError(
                f"{name} requires /{prefix}, which is larger than root capacity {root}."
            )
        normalized.append((name.strip(), hosts, prefix))

    # Largest subnet first is essential for contiguous VLSM allocation.
    normalized.sort(key=lambda row: row[1], reverse=True)
    cursor = int(root.network_address)
    root_end = int(root.broadcast_address)
    allocations: list[SubnetAllocation] = []

    for name, hosts, prefix in normalized:
        block_size = 1 << (32 - prefix)
        aligned = ((cursor + block_size - 1) // block_size) * block_size
        end = aligned + block_size - 1
        if aligned > root_end or end > root_end:
            raise AddressSpaceExhaustedError(
                f"Address space exhausted while allocating {name} ({hosts} hosts, /{prefix}) "
                f"inside {root}."
            )

        subnet = ipaddress.IPv4Network((aligned, prefix))
        if not subnet.subnet_of(root):
            raise AddressSpaceExhaustedError(f"Allocated subnet {subnet} is outside {root}.")

        usable = subnet.num_addresses - 2
        first = subnet.network_address + 1
        last = subnet.broadcast_address - 1
        utilization = (hosts / usable) * 100 if usable else 0.0
        allocations.append(SubnetAllocation(
            name=name,
            requested_hosts=hosts,
            network=str(subnet),
            prefix=prefix,
            subnet_mask=str(subnet.netmask),
            wildcard_mask=wildcard_from_prefix(prefix),
            network_address=str(subnet.network_address),
            first_usable=str(first),
            gateway=str(first),
            last_usable=str(last),
            broadcast_address=str(subnet.broadcast_address),
            total_addresses=subnet.num_addresses,
            usable_addresses=usable,
            utilization_percent=round(utilization, 2)
        ))
        cursor = end + 1

    # Defensive invariant checks: no overlaps and all allocations inside root.
    networks = [ipaddress.ip_network(item.network) for item in allocations]
    for i, net in enumerate(networks):
        if not net.subnet_of(root):
            raise AssertionError(f"Internal allocator error: {net} outside {root}.")
        for other in networks[i + 1:]:
            if net.overlaps(other):
                raise AssertionError(f"Internal allocator error: {net} overlaps {other}.")
    return allocations
