from dataclasses import dataclass

@dataclass(frozen=True)
class TopologyRecommendation:
    topology: str
    layers_or_domains: list[str]
    rationale: str
    caveats: list[str]

def recommend_topology(profile: str, sites: int, buildings: int,
                       redundancy_required: bool) -> TopologyRecommendation:
    if sites < 1 or buildings < 1:
        raise ValueError("Sites and buildings must both be at least 1.")
    if profile == "campus_lan":
        return TopologyRecommendation(
            "Hierarchical campus LAN (core/distribution/access)",
            ["Core", "Distribution", "Access"],
            f"A campus with {buildings} building(s) benefits from separating backbone, aggregation and endpoint access functions.",
            ["A collapsed core may be suitable depending on actual scale.", "The assignment does not prescribe exact switch counts or placement."])
    if profile == "metro_man":
        return TopologyRecommendation(
            "Metro Ethernet hub-and-spoke with dual-homed site connectivity",
            ["Headquarters", "Remote sites", "Provider EVPL services"],
            f"The MAN profile connects {sites} sites over 15–35 km links; dual-homed connectivity supports the stated resiliency objective.",
            ["Carrier path diversity must be confirmed.", "The sub-5 ms target requires measurement and cannot be guaranteed by topology alone."])
    if profile == "global_wan":
        return TopologyRecommendation(
            "Distributed enterprise WAN with cloud connectivity",
            ["City networks", "WAN routing domains", "Cloud VPC"],
            "Four cities and a cloud VPC require distributed WAN connectivity, explicit routing boundaries and secure inter-site connectivity.",
            ["Exact hub/mesh design depends on traffic and provider requirements.", "IPsec and cloud routing parameters must be supplied."])
    return TopologyRecommendation("Custom topology (requirements-driven)", ["User-defined"],
        "No preset topology is assumed for a custom scenario.",
        ["Provide site relationships, device roles and resiliency requirements."])
