def recommend_redundancy(required: bool, profile: str, sites: int) -> dict:
    if sites < 1:
        raise ValueError("At least one site is required.")
    if not required:
        return {"enabled": False, "design": "Single-path baseline",
            "recommendations": ["Document single points of failure.", "Do not claim high availability without redundant paths and devices."],
            "rationale": "Redundancy was not requested in the supplied scenario."}
    if profile == "metro_man":
        design = "Dual-homed WAN connectivity"
        recommendations = ["Use two independently provisioned provider paths where available.",
            "Define primary/backup or active/active routing behavior.",
            "Test link failure, route withdrawal and recovery.",
            "Confirm physical path diversity with the carrier."]
    elif profile == "global_wan":
        design = "Redundant WAN/VPN paths"
        recommendations = ["Provide redundant WAN or VPN termination where supported.",
            "Define routing convergence and failover policy.",
            "Test tunnel failure and alternate-path recovery."]
    else:
        design = "Redundant campus uplinks and resilient switching"
        recommendations = ["Provide redundant uplinks between access, distribution and core.",
            "Use an appropriate loop-prevention mechanism such as Rapid PVST+.",
            "Test link failure and avoid unintended Layer 2 loops."]
    return {"enabled": True, "design": design, "recommendations": recommendations,
        "rationale": f"Resiliency was requested for {profile.replace('_', ' ')}; alternate connectivity and an explicit failover test plan are recommended."}
