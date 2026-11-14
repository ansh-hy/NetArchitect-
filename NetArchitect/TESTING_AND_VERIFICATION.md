# Testing, Verification and Quality Assurance

## Automated unit and integration tests

Run from the project root:

```bash
pytest -v
```

Optional coverage report:

```bash
pytest --cov=core --cov=generators --cov-report=term-missing
```

Test groups cover:

- Physical medium boundaries: 100 m, 101 m, 400 m and above 400 m.
- Explicit copper request beyond 100 m.
- Negative, non-numeric, NaN and infinite distances.
- VLAN ID range, duplicate IDs, duplicate names and empty names.
- VLSM prefix calculation, wildcard masks, largest-first order, network/broadcast/gateway, root containment, overlap and address exhaustion.
- Routing boundaries: 49 versus 50 subnets, multi-site/cloud and external-AS conditions.
- All three presets through the full analysis pipeline.
- Generated configuration invariants: OSPF on the SVI gateway device for Campus LAN, no fabricated multi-area mapping, no unapproved permissive ACL.
- Explainability and output artifacts.

## Release verification

```bash
python scripts/verify_release.py
```

The script re-runs all three presets, validates expected outputs and checks generated export files.

## Manual simulator verification required

Automated tests validate Python logic and rendered text. They do not emulate Cisco IOS or transmit packets. Complete the steps in `PACKET_TRACER_GNS3_GUIDE.md` and record the simulator version, device models, topology file name, test date and ping/CLI evidence.

## Required packet-flow test matrix

| Test ID | Source | Destination | Expected result | Evidence |
|---|---|---|---|---|
| PT-01 | PC-A in VLAN 10 | PC-B in VLAN 10 | Ping succeeds | Ping output |
| PT-02 | PC in VLAN 10 | Server VLAN host | Succeeds if routing/policy permits | Ping + `show ip route` |
| PT-03 | VLAN 10 host | VLAN 30 host | Inter-VLAN routing succeeds unless explicit policy denies | Ping + SVI state |
| PT-04 | Campus L3 switch | Remote routed test subnet | Route appears after OSPF adjacency | `show ip ospf neighbor`, `show ip route` |
| PT-05 | One redundant uplink | Disconnect/fail link | Traffic recovers over surviving path | Before/after ping and STP/EtherChannel state |
| PT-06 | Metro HQ | Remote site | Reachability over EVPL path | Ping/traceroute; measured latency |
| PT-07 | Global city site | Cloud VPC test host | Reachability through configured IPsec path | VPN state + ping + route |
| PT-08 | Management source | Unapproved destination/service | Denied by the final explicitly designed ACL | ACL counters and packet test |

Do not mark a test as passed until it has been executed on the simulator. Record actual outcomes in `verification/simulator_results_template.md`.
