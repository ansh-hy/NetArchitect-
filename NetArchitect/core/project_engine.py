"""Orchestrates all deterministic engines for a validated scenario."""
from core.media_engine import select_media
from core.vlan_engine import build_vlan_plan
from core.topology_engine import recommend_topology
from core.redundancy_engine import recommend_redundancy
from core.vlsm_engine import allocate_vlsm
from core.routing_engine import select_routing
from core.explainability_engine import build_decision_report
from generators.config_generator import generate_config_bundle


def analyze_scenario(scenario):
    media = select_media(scenario.max_link_distance_m)
    vlans = build_vlan_plan([v.model_dump() for v in scenario.vlan_requirements])
    topology = recommend_topology(
        scenario.profile, scenario.sites, scenario.buildings,
        scenario.redundancy_required
    )
    redundancy = recommend_redundancy(
        scenario.redundancy_required, scenario.profile, scenario.sites
    )
    if not scenario.subnet_requirements:
        raise ValueError(
            "No subnet host requirements were supplied. Add subnet_requirements before running VLSM."
        )
    subnets = allocate_vlsm(
        str(scenario.root_network),
        [s.model_dump() for s in scenario.subnet_requirements]
    )
    routing = select_routing(
        scenario.subnet_count, scenario.multi_site, scenario.cloud_boundary,
        scenario.external_as_boundary
    )
    report = build_decision_report(
        scenario, media, vlans, topology, redundancy, subnets, routing
    )
    configs = generate_config_bundle(scenario, vlans, subnets, routing)
    return {
        "media": media, "vlans": vlans, "topology": topology,
        "redundancy": redundancy, "subnets": subnets,
        "routing": routing, "decision_report": report,
        "configurations": configs
    }
