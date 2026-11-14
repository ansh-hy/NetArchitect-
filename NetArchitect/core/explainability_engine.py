"""Deterministic engineering rationale builder; explanations derive from engine outputs."""
from dataclasses import asdict


def build_decision_report(scenario, media, vlan_plan, topology, redundancy,
                          subnet_allocations, routing) -> dict:
    decisions = [
        {
            "area": "Physical media",
            "selection": f"{media.media} with {media.transceiver}",
            "input_basis": f"Maximum supplied link distance: {media.distance_m:g} m",
            "rationale": media.rationale,
            "transceiver_rationale": (
                "10GBASE-T is the copper PHY; 10GBASE-SR uses short-reach multimode optics "
                "(850 nm); 10GBASE-LR/ER are single-mode reach classes whose exact choice "
                "depends on distance and the calculated optical loss budget."
            ),
            "reference": media.standard_reference
        },
        {
            "area": "Topology",
            "selection": topology.topology,
            "input_basis": (
                f"Profile={scenario.profile}; sites={scenario.sites}; buildings={scenario.buildings}; "
                f"endpoints={scenario.endpoints}; average endpoints/building="
                f"{scenario.endpoints / scenario.buildings:.2f}"
            ),
            "rationale": topology.rationale,
            "tier_rationale": (
                "Campus: core/distribution/access separates backbone, aggregation and endpoint access. "
                "Metro: provider Ethernet links connect HQ and remote sites with diverse paths where available. "
                "Global: distributed WAN routing connects city networks and the cloud routing domain."
            ),
            "reference": "Assignment scenario; IEEE 802.1Q (VLAN tagging) and IEEE 802.1w (RSTP) where applicable"
        },
        {
            "area": "Routing",
            "selection": routing.protocol,
            "input_basis": f"Subnets={scenario.subnet_count}; multi_site={scenario.multi_site}; cloud_boundary={scenario.cloud_boundary}",
            "rationale": routing.rationale,
            "reference": routing.reference
        },
        {
            "area": "Redundancy",
            "selection": redundancy["design"],
            "input_basis": f"Redundancy requested={scenario.redundancy_required}",
            "rationale": redundancy["rationale"],
            "reference": "Assignment resiliency scenario requirements"
        }
    ]

    if scenario.multi_site or scenario.cloud_boundary:
        decisions.append({
            "area": "Route summarization",
            "selection": f"Site-specific aggregate prefixes required within {scenario.root_network}",
            "input_basis": (
                f"Multi-site={scenario.multi_site}; cloud boundary={scenario.cloud_boundary}; "
                f"root pool={scenario.root_network}"
            ),
            "rationale": (
                "Summarization reduces inter-domain route table size, but the input only supplies one "
                "overall address pool and no site-to-prefix allocation. A safe per-site summary cannot "
                "be emitted until non-overlapping site aggregates and route ownership are defined."
            ),
            "reference": "Assignment Global WAN requirement: route summarization"
        })

    if vlan_plan:
        decisions.append({
            "area": "VLAN segmentation",
            "selection": f"{len(vlan_plan)} validated VLANs",
            "input_basis": ", ".join(f"VLAN {v.vlan_id} {v.name}" for v in vlan_plan),
            "rationale": "VLANs are taken from the scenario's explicit segmentation requirements; unique IDs and names are validated.",
            "reference": "IEEE 802.1Q"
        })

    for subnet in subnet_allocations:
        host_bits = 32 - subnet.prefix
        decisions.append({
            "area": f"VLSM – {subnet.name}",
            "selection": subnet.network,
            "input_basis": f"{subnet.requested_hosts} requested hosts",
            "rationale": (
                f"Choose h={host_bits} host bits so 2^{host_bits} - 2 >= {subnet.requested_hosts}; "
                f"prefix = 32 - {host_bits} = /{subnet.prefix}. The block has {subnet.total_addresses} "
                f"addresses and {subnet.usable_addresses} conventional usable addresses. "
                f"Gateway is first usable {subnet.gateway}; utilization = "
                f"{subnet.requested_hosts}/{subnet.usable_addresses} x 100 = "
                f"{subnet.utilization_percent}%."
            ),
            "reference": "RFC 950 (Internet Standard Subnetting Procedure); RFC 4632 (CIDR); IPv4 network/broadcast reservation for conventional LAN subnets"
        })

    return {
        "scenario": scenario.name,
        "profile": scenario.profile,
        "decisions": decisions,
        "topology_caveats": topology.caveats,
        "routing_caveats": routing.caveats,
        "redundancy_actions": redundancy["recommendations"],
        "engineering_assumptions": [
            "VLSM gateway policy is first usable IPv4 address.",
            "Conventional LAN subnetting reserves network and broadcast addresses.",
            "Media distance bands follow the assignment; final optics require compatibility and optical-budget verification.",
            "Recommendations are design outputs and do not prove live network performance."
        ]
    }
