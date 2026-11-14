import json
import zipfile
from io import BytesIO

import pandas as pd
import streamlit as st

from core.scenario_manager import load_preset, list_presets
from core.input_validator import validate_scenario
from core.project_engine import analyze_scenario

st.set_page_config(page_title="NetArchitect", page_icon="🌐", layout="wide")
st.title("🌐 NetArchitect")
st.caption("Algorithmic Network Planning & Self-Explaining Architecture Engine")

with st.sidebar:
    st.header("Network design")
    mode = st.radio("Input source", ["Preset scenario", "Custom scenario"])
    scenario_data = None

    if mode == "Preset scenario":
        selected = st.selectbox(
            "Choose profile", list_presets(),
            format_func=lambda x: x.replace("_", " ").title()
        )
        scenario_data = load_preset(selected)
    else:
        st.subheader("General parameters")
        name = st.text_input("Scenario name", "My Enterprise Network")
        profile = st.selectbox("Profile", ["campus_lan", "metro_man", "global_wan", "custom"])
        sites = st.number_input("Sites", 1, 100, 1)
        buildings = st.number_input("Buildings", 1, 500, 1)
        endpoints = st.number_input("Endpoints", 1, 1_000_000, 100)
        distance = st.number_input("Maximum link distance (m)", 0.0, 10_000_000.0, 100.0)
        root = st.text_input("Root IPv4 network", "10.0.0.0/16")
        subnet_count = st.number_input("Routing subnet count", 1, 4094, 5)
        bandwidth = st.number_input("Required bandwidth (Mbps)", 1, 10_000_000, 1000)
        multi_site = st.checkbox("Multiple routing sites")
        cloud_boundary = st.checkbox("Cloud routing boundary")
        external_as = st.checkbox("External autonomous-system boundary")
        redundancy_required = st.checkbox("Redundancy required")
        st.caption("Enter one subnet per line as NAME,HOSTS.")
        subnet_text = st.text_area(
            "Subnet host requirements",
            "ADMIN,100\nUSERS,500\nSERVERS,50",
            height=110
        )
        st.caption("Enter VLANs as ID,NAME,PURPOSE; one per line.")
        vlan_text = st.text_area(
            "VLAN requirements",
            "10,ADMIN,Administration\n20,USERS,Users\n30,SERVERS,Servers",
            height=110
        )
        subnet_requirements = []
        for line_no, line in enumerate(subnet_text.splitlines(), 1):
            if not line.strip():
                continue
            parts = [p.strip() for p in line.split(",", 1)]
            if len(parts) != 2:
                st.error(f"Subnet line {line_no}: use NAME,HOSTS.")
                continue
            try:
                subnet_requirements.append({"name": parts[0], "hosts": int(parts[1])})
            except ValueError:
                st.error(f"Subnet line {line_no}: host count must be an integer.")
        vlan_requirements = []
        for line_no, line in enumerate(vlan_text.splitlines(), 1):
            if not line.strip():
                continue
            parts = [p.strip() for p in line.split(",", 2)]
            if len(parts) < 2:
                st.error(f"VLAN line {line_no}: use ID,NAME,PURPOSE.")
                continue
            try:
                vlan_requirements.append({
                    "vlan_id": int(parts[0]), "name": parts[1],
                    "purpose": parts[2] if len(parts) > 2 else "General"
                })
            except ValueError:
                st.error(f"VLAN line {line_no}: VLAN ID must be an integer.")

        scenario_data = {
            "name": name, "profile": profile, "sites": int(sites),
            "buildings": int(buildings), "endpoints": int(endpoints),
            "max_link_distance_m": float(distance), "root_network": root,
            "subnet_count": int(subnet_count),
            "required_bandwidth_mbps": int(bandwidth),
            "multi_site": multi_site, "cloud_boundary": cloud_boundary,
            "external_as_boundary": external_as,
            "redundancy_required": redundancy_required,
            "vlan_requirements": vlan_requirements,
            "subnet_requirements": subnet_requirements
        }

    run = st.button("Analyze network", type="primary", use_container_width=True)

if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
if "scenario_snapshot" not in st.session_state:
    st.session_state.scenario_snapshot = None

if run:
    try:
        validated = validate_scenario(scenario_data)
        result = analyze_scenario(validated)
        st.session_state.analysis_result = result
        st.session_state.scenario_snapshot = validated
        st.success("Network analysis completed. Review the tabs below.")
    except Exception as exc:
        st.session_state.analysis_result = None
        st.error(f"Analysis could not be completed: {exc}")

result = st.session_state.analysis_result
scenario = st.session_state.scenario_snapshot

if result and scenario:
    media = result["media"]
    routing = result["routing"]
    subnets = result["subnets"]
    st.subheader(f"Analysis: {scenario.name}")
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Endpoints", f"{scenario.endpoints:,}")
    k2.metric("Sites", scenario.sites)
    k3.metric("Buildings", scenario.buildings)
    k4.metric("Avg. endpoints / building", f"{scenario.endpoints / scenario.buildings:.1f}")
    k5.metric("Allocated subnets", len(subnets))
    st.caption(f"Root IPv4 allocation pool: {scenario.root_network}")

    overview, architecture, addressing, explanations, configs, validation = st.tabs([
        "Overview", "Architecture", "IP Addressing", "Decision Rationale",
        "Cisco Configurations", "Validation"
    ])

    with overview:
        st.subheader("Engineering recommendations")
        a, b = st.columns(2)
        with a:
            st.metric("Physical medium", media.media)
            st.write(f"**Transceiver:** {media.transceiver}")
            st.write(media.rationale)
        with b:
            st.metric("Routing recommendation", routing.protocol)
            st.write(routing.rationale)
        st.subheader("VLAN segmentation")
        if result["vlans"]:
            st.dataframe(pd.DataFrame([v.__dict__ for v in result["vlans"]]),
                         use_container_width=True, hide_index=True)
        else:
            st.info("No VLANs were specified. Add VLAN requirements to generate VLAN/SVI configuration.")

    with architecture:
        st.subheader("Recommended topology")
        st.markdown(f"**{result['topology'].topology}**")
        st.write(result["topology"].rationale)
        st.markdown("**Layers / routing domains**")
        st.write(" → ".join(result["topology"].layers_or_domains))
        st.markdown("**Design caveats**")
        for caveat in result["topology"].caveats:
            st.warning(caveat)
        st.subheader("Redundancy and failover plan")
        st.markdown(f"**{result['redundancy']['design']}**")
        st.write(result["redundancy"]["rationale"])
        for item in result["redundancy"]["recommendations"]:
            st.write(f"• {item}")
        st.subheader("Routing decision")
        st.markdown(f"**{routing.protocol}**")
        for caveat in routing.caveats:
            st.warning(caveat)

    with addressing:
        st.subheader("VLSM allocation")
        subnet_rows = [{
            "Subnet": s.name, "Required hosts": s.requested_hosts,
            "Network / Prefix": s.network, "Subnet mask": s.subnet_mask,
            "Wildcard mask": s.wildcard_mask, "Gateway": s.gateway,
            "First usable": s.first_usable, "Last usable": s.last_usable,
            "Broadcast": s.broadcast_address, "Usable capacity": s.usable_addresses,
            "Utilization (%)": s.utilization_percent
        } for s in subnets]
        st.dataframe(pd.DataFrame(subnet_rows), use_container_width=True, hide_index=True)
        st.caption("Allocation is largest-subnet-first. Conventional LAN network and broadcast addresses are reserved; gateway policy is first usable IP.")
        csv_data = pd.DataFrame(subnet_rows).to_csv(index=False).encode("utf-8")
        st.download_button("Download subnet allocation CSV", csv_data,
                           "vlsm_allocations.csv", "text/csv")

    with explanations:
        st.subheader("Explainable engineering decisions")
        for decision in result["decision_report"]["decisions"]:
            with st.expander(f"{decision['area']}: {decision['selection']}", expanded=False):
                st.markdown(f"**Input basis:** {decision['input_basis']}")
                st.write(decision["rationale"])
                for detail_key in ("transceiver_rationale", "tier_rationale"):
                    if decision.get(detail_key):
                        st.info(decision[detail_key])
                st.caption(f"Technical reference/basis: {decision['reference']}")
        st.subheader("Assumptions and limitations")
        for assumption in result["decision_report"]["engineering_assumptions"]:
            st.write(f"• {assumption}")

    with configs:
        st.subheader("Generated Cisco IOS configuration files")
        st.warning("Review device model, IOS version, interfaces, addressing, routing areas, ACL policy and provider details before deployment. These are generated configuration baselines, not proof of device-tested configurations.")
        for filename, content in result["configurations"].items():
            with st.expander(filename):
                st.code(content, language="text")
                st.download_button(f"Download {filename}", content,
                                   filename, "text/plain", key=f"download_{filename}")
        bundle = BytesIO()
        with zipfile.ZipFile(bundle, "w", zipfile.ZIP_DEFLATED) as archive:
            for filename, content in result["configurations"].items():
                archive.writestr(filename, content)
            archive.writestr("decision_report.json",
                             json.dumps(result["decision_report"], indent=2))
        st.download_button("Download complete configuration and report bundle",
                           bundle.getvalue(), "netarchitect_exports.zip",
                           "application/zip")

    with validation:
        st.subheader("Automated design checks")
        checks = [
            ("Input schema", "Passed", "Pydantic accepted the scenario."),
            ("VLSM containment", "Passed", "All allocations fit inside the selected root prefix."),
            ("VLSM overlap", "Passed", "Allocator verifies every pair of allocated subnets."),
            ("VLAN uniqueness", "Passed", "VLAN IDs and names are checked for duplicates."),
            ("Configuration generation", "Generated", "IOS template outputs were rendered."),
            ("Device simulation", "Not run", "Load the exports into Packet Tracer/GNS3 and verify against your target device model.")
        ]
        st.dataframe(pd.DataFrame(checks, columns=["Check", "Status", "Details"]),
                     use_container_width=True, hide_index=True)
        st.caption("A generated configuration is not considered Packet Tracer/GNS3 verified until you perform and document that simulation.")
else:
    st.info("Choose a preset or enter custom parameters in the sidebar, then select **Analyze network**.")
    st.markdown("""
    **Available profiles**
    - **Campus LAN:** three buildings, 1,600 endpoints, VLANs, RSTP and single-area OSPF conditions.
    - **Metro MAN:** headquarters plus two remote sites, EVPL, low-latency target and dual-homed resiliency.
    - **Global WAN:** four cities plus cloud VPC, IPsec VPN and multi-domain routing.

    Use the tabs after analysis to inspect architecture, VLSM allocations, technical reasoning and Cisco configuration exports.
    """)
