# NetArchitect — System Architecture

## 1. Architectural objective

NetArchitect is an explainable automated network architect, not merely a subnet calculator or CLI text generator. It ingests a preset or custom scenario, evaluates requirements through deterministic decision engines, computes addressing, recommends topology and routing, produces configuration artifacts, and records why each decision was made.

## 2. Layered architecture

```mermaid
flowchart TD
    A[Streamlit UI / Preset JSON / Custom Input] --> B[Pydantic Input Validation]
    B --> C[Scenario Orchestrator]
    C --> D[L1 Media Engine]
    C --> E[L2 VLAN Engine]
    C --> F[Topology Engine]
    C --> G[Redundancy Engine]
    C --> H[L3 VLSM Allocator]
    C --> I[Routing Decision Engine]
    D --> J[Explainability Engine]
    E --> J
    F --> J
    G --> J
    H --> J
    I --> J
    D --> K[Jinja2 Config Generator]
    E --> K
    H --> K
    I --> K
    J --> L[Decision Report / UI]
    K --> M[IOS Configs / CSV / ZIP]
    C --> N[Pytest Regression Suite]
```

## 3. Core modules

| Module | Responsibility | Main checks/output |
|---|---|---|
| `models.py` | Typed scenario and requirement schemas | Types, bounds, IPv4 root |
| `input_validator.py` | Validates preset/custom input | Pydantic validation errors |
| `media_engine.py` | Cat6a/OM4/OS2 selection | 100 m and 400 m bands; copper violation |
| `vlan_engine.py` | VLAN plan validation | ID range, duplicate IDs/names |
| `topology_engine.py` | Profile-specific architecture recommendation | Campus/MAN/WAN rationale and caveats |
| `redundancy_engine.py` | Resiliency recommendations | Dual path, uplink and failover test guidance |
| `vlsm_engine.py` | Bitwise IPv4 VLSM allocation | Largest-first, masks, wildcard, gateway, broadcast, capacity, overlap |
| `routing_engine.py` | OSPF/Multi-Area OSPF/eBGP choice | Assignment conditions and unresolved cases |
| `explainability_engine.py` | Decision trace | Input basis, choice, rationale, reference, assumptions |
| `config_generator.py` | Renders Jinja2 IOS artifacts | Switch, SVI, router, ACL, IPsec planning and route-summarization outputs |
| `project_engine.py` | Coordinates all engines | Single analysis result object |

## 4. End-to-end decision flow

1. User selects Campus LAN, Metro MAN, Global WAN or Custom.
2. Pydantic validates field types and allowed ranges.
3. L1 engine selects medium from the maximum link distance:
   - 0–100 m: Cat6a / 10GBASE-T
   - 101–400 m: OM4 / 10GBASE-SR / 850 nm
   - over 400 m: OS2 / 10GBASE-LR/ER, with optical-budget verification required
4. L2 engine validates VLAN IDs and names.
5. Topology and redundancy engines select the profile design and explain caveats.
6. VLSM sorts host requests descending and allocates aligned non-overlapping blocks.
7. Routing engine applies the assignment's routing decision conditions.
8. Explainability engine records every selected decision and the supplied input basis.
9. Jinja2 renders configuration baselines only where the input is sufficient.
10. User downloads the report, subnet table and configuration bundle.
11. Pytest checks calculations, boundaries and generated output invariants.

## 5. Campus LAN logical architecture

```mermaid
flowchart TD
    ISP[ISP / Internet] --> EDGE[Edge Router / Firewall]
    EDGE --> CORE[Core Layer 3 Switch]
    CORE --> D1[Building 1 Distribution]
    CORE --> D2[Building 2 Distribution]
    CORE --> D3[Building 3 Distribution]
    D1 --> A1[Access Switches / PoE APs]
    D2 --> A2[Access Switches / PoE APs]
    D3 --> A3[Access Switches / PoE APs]
    A1 --> C1[Campus Endpoints]
    A2 --> C2[Campus Endpoints]
    A3 --> C3[Campus Endpoints]
    CORE --> SRV[Server VLAN]
```

Redundant uplinks should be physically diverse where possible and controlled with an appropriate Layer 2 loop-prevention or routed design. Exact device count and port mapping depend on endpoint placement and selected hardware.

## 6. Metro MAN logical architecture

```mermaid
flowchart LR
    HQ[Headquarters] --> PE1[Provider Edge / EVPL]
    PE1 --> R1[Remote Site 1]
    HQ --> PE2[Independent Provider Path]
    PE2 --> R2[Remote Site 2]
    R1 -. alternate path subject to carrier design .- R2
```

The assignment specifies HQ plus two remote sites, 15–35 km, EVPL, sub-5 ms target and dual-homed failover. Carrier path diversity and measured latency must be confirmed; topology alone cannot guarantee the latency target.

## 7. Global WAN logical architecture

```mermaid
flowchart TD
    C1[City 1] --> WAN[Enterprise WAN Routing]
    C2[City 2] --> WAN
    C3[City 3] --> WAN
    C4[City 4] --> WAN
    WAN --> VPN[IPsec VPN Boundary]
    VPN --> CLOUD[Cloud VPC]
```

The assignment calls for four cities plus a Cloud VPC, IPsec VPN, multi-area OSPF/BGP and route summarization. Actual BGP peerings, AS numbers, VPN endpoints, crypto suites and prefix policies require deployment-specific inputs.

## 8. Important design boundaries

- Preset data in the assignment does not specify exact device models, IOS versions or interface inventories.
- It does not provide OSPF area IDs/subnet-to-area mappings, ABR placement, BGP ASNs/peer addresses/policies, or a least-privilege ACL policy.
- The program must explain these missing inputs and avoid inventing production configuration.
- A generated config is not simulator-verified until loaded into Packet Tracer/GNS3 and tested.
