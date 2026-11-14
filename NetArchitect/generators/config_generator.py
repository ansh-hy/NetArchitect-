"""Cisco IOS configuration generation from validated scenario and VLSM data."""
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, StrictUndefined


def _safe_hostname(value: str) -> str:
    import re
    slug = re.sub(r"[^A-Za-z0-9-]", "-", value.strip()).strip("-").upper()
    return (slug or "NETARCHITECT")[:32]


def generate_config_bundle(scenario, vlan_plan, subnet_allocations, routing) -> dict[str, str]:
    template_dir = Path(__file__).resolve().parent.parent / "templates"
    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True
    )
    vlans = [v.__dict__ for v in vlan_plan]
    subnets = [s.__dict__ for s in subnet_allocations]
    vlan_by_name = {v["name"].strip().lower(): v for v in vlans}
    subnet_rows = []
    for subnet in subnets:
        vlan = vlan_by_name.get(subnet["name"].strip().lower())
        subnet_rows.append({**subnet, "vlan_id": vlan["vlan_id"] if vlan else None,
                            "vlan_name": vlan["name"] if vlan else None})

    context = {
        "hostname": _safe_hostname(scenario.name),
        "vlans": vlans,
        "subnets": subnet_rows,
        "routing": routing,
        "root_network": str(scenario.root_network),
        "scenario_vpn_required": scenario.vpn_required,
        "multi_site": scenario.multi_site,
        "cloud_boundary": scenario.cloud_boundary,
        "management_subnet": next(
            (s for s in subnet_rows if "management" in s["name"].lower()), None
        )
    }

    outputs = {}
    for filename, output_name in [
        ("switch_template.j2", "switches.cfg"),
        ("router_template.j2", "routers.cfg"),
        ("svi_template.j2", "svis.cfg"),
        ("acl_template.j2", "acls.cfg"),
        ("vpn_template.j2", "vpn.cfg"),
        ("route_summary_template.j2", "route_summarization.cfg")
    ]:
        outputs[output_name] = env.get_template(filename).render(**context).strip() + "\n"
    return outputs
