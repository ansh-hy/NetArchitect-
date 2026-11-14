"""Rule-based routing recommendations aligned to the assignment decision table."""
from dataclasses import dataclass


@dataclass(frozen=True)
class RoutingRecommendation:
    protocol: str
    routing_scope: str
    rationale: str
    conditions: list[str]
    caveats: list[str]
    reference: str


def select_routing(subnet_count: int, multi_site: bool = False,
                   cloud_boundary: bool = False,
                   external_as_boundary: bool = False) -> RoutingRecommendation:
    if isinstance(subnet_count, bool) or not isinstance(subnet_count, int) or subnet_count < 1:
        raise ValueError("Subnet count must be a positive integer.")

    if multi_site or cloud_boundary:
        if external_as_boundary:
            return RoutingRecommendation(
                "eBGP",
                "Between independently administered autonomous systems",
                "eBGP is recommended because the input explicitly identifies an external autonomous-system boundary.",
                ["External AS boundary is explicitly true."],
                ["Requires AS numbers, peer addresses, policy, authentication and provider coordination."],
                "RFC 4271 (BGP-4)"
            )
        return RoutingRecommendation(
            "Multi-Area OSPF (internal) with eBGP where an external AS boundary exists",
            "Multi-site / multi-cloud routing domains",
            "The multi-site or cloud-boundary condition requires a scalable routing design. Use Multi-Area OSPF inside the enterprise routing domain; use eBGP only across a genuine external autonomous-system boundary.",
            ["Multiple sites or cloud boundary is present."],
            ["The assignment allows Multi-Area OSPF or eBGP for this condition; the precise choice depends on whether the peer is in the same or a different AS."],
            "RFC 2328 (OSPFv2); RFC 4271 (BGP-4) where an external AS peering exists"
        )

    if subnet_count < 50:
        return RoutingRecommendation(
            "OSPF Area 0",
            "Single autonomous system",
            f"OSPF Area 0 is selected because the network is a single autonomous system with {subnet_count} subnets, below the assignment's 50-subnet threshold.",
            ["Single routing domain.", "Subnet count is less than 50."],
            ["If the network grows to multiple sites or external routing domains, reassess the routing design."],
            "RFC 2328 (OSPFv2)"
        )

    return RoutingRecommendation(
        "Routing design review required",
        "Single autonomous system with 50 or more subnets",
        f"The assignment specifies OSPF Area 0 for a single AS with fewer than 50 subnets, but does not prescribe a protocol for this case ({subnet_count} subnets).",
        ["Single AS.", "Subnet count is 50 or greater."],
        ["Do not silently assume the assignment's <50 rule applies; obtain a design decision or define an approved extension."],
        "RFC 2328 (OSPFv2) / RFC 4271 (BGP-4), subject to approved design"
    )
