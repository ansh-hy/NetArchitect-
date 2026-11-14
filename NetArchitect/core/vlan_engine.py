from dataclasses import dataclass

@dataclass(frozen=True)
class VLANPlan:
    vlan_id: int
    name: str
    purpose: str

def build_vlan_plan(requirements: list[dict]) -> list[VLANPlan]:
    if not isinstance(requirements, list):
        raise TypeError("VLAN requirements must be a list.")
    plans, seen_ids, seen_names = [], set(), set()
    for item in requirements:
        if not isinstance(item, dict):
            raise ValueError("Each VLAN requirement must be an object.")
        vlan_id, name = item.get("vlan_id"), item.get("name")
        purpose = item.get("purpose", "General")
        if isinstance(vlan_id, bool) or not isinstance(vlan_id, int):
            raise ValueError("VLAN ID must be an integer.")
        if not 1 <= vlan_id <= 4094:
            raise ValueError(f"VLAN ID {vlan_id} is outside usable range 1–4094.")
        if not isinstance(name, str) or not name.strip():
            raise ValueError("VLAN name must be a non-empty string.")
        normalized = name.strip().lower()
        if vlan_id in seen_ids:
            raise ValueError(f"Duplicate VLAN ID: {vlan_id}.")
        if normalized in seen_names:
            raise ValueError(f"Duplicate VLAN name: {name}.")
        seen_ids.add(vlan_id)
        seen_names.add(normalized)
        plans.append(VLANPlan(vlan_id, name.strip(), str(purpose)))
    return sorted(plans, key=lambda vlan: vlan.vlan_id)
