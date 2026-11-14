# Packet Tracer / GNS3 Verification Guide

## Why this step is separate

NetArchitect generates IOS configuration text and verifies algorithms with pytest. The supplied assignment additionally asks for three preset exports loaded into Packet Tracer or GNS3. A simulator project must be assembled with supported device images/models; a `.cfg` file is not itself a topology file.

## Campus LAN — recommended lab

### Logical devices
- 1 edge router (or router/firewall representation)
- 1 multilayer switch for core and VLAN gateways
- 3 distribution switches (one per building)
- Access switches sized to the lab endpoint sample
- 1 server and at least 2 PCs per VLAN under test

A Packet Tracer lab is a scaled functional demonstration, not a literal 1,600-PC deployment. Use representative endpoints and document the scale model.

### Build and configure
1. Create a new Packet Tracer project and save it under `verification/labs/campus_lan/`.
2. Place the core multilayer switch, three distribution switches, access switches, edge router, server and representative PCs.
3. Connect core-to-distribution and distribution-to-access links. Use redundant uplinks only with a loop-prevention design (Rapid PVST+ or a routed alternative).
4. Open `exports/campus_lan/switches.cfg`; apply VLAN and trunk commands to the correct Layer 2 switches after checking their actual interface names.
5. Open `exports/campus_lan/svis.cfg`; apply SVI and OSPF commands to the multilayer gateway switch. Check model support for `ip routing` and OSPF.
6. Open `exports/campus_lan/routers.cfg`; note that WAN/edge interface addressing and ISP routing are intentionally not generated because the assignment has no interface inventory or ISP parameters.
7. Review `exports/campus_lan/acls.cfg`; no ACL permit policy is generated until the security policy is specified.
8. Assign endpoint IPs, masks and default gateways from `exports/campus_lan/vlsm_allocations.json`.
9. Run `show vlan brief`, `show interfaces trunk`, `show ip interface brief`, `show ip route`, `show ip ospf neighbor` and `show spanning-tree`.
10. Run the Campus tests in `TESTING_AND_VERIFICATION.md`; record actual results.

## Metro MAN
1. Create `verification/labs/metro_man/`.
2. Model HQ and two remote sites with routers and provider Ethernet/cloud objects.
3. Represent primary and alternate EVPL paths only if the simulator topology supports the intended path model.
4. Apply VLAN/L2 outputs to appropriate site switches.
5. Do not configure a fictional Multi-Area OSPF plan: supply area IDs, ABR locations and subnet-to-area mappings first.
6. Measure end-to-end latency in the chosen environment; a topology diagram cannot prove the assignment's sub-5 ms target.
7. Simulate primary-path failure and document recovery.

## Global WAN
1. Create `verification/labs/global_wan/`.
2. Represent four city sites and a cloud VPC/remote VPN endpoint.
3. Configure IPsec only after selecting supported device models, IKE/IPsec parameters, peer IPs, authentication material and protected prefixes.
4. Configure eBGP only after assigning local/peer ASNs, neighbor IPs, address families and route policies.
5. Validate summarization and route propagation with route tables and traceroute.
6. Simulate tunnel/path failure and document alternate connectivity.

## Evidence to capture
For each preset, save:
- Topology screenshot with device labels and link roles.
- Relevant `show` command output.
- Successful and intentionally failed ping tests.
- Failover test output.
- Simulator name/version and device model list.
- Any configuration changes made to adapt generated baselines.

**Do not describe a preset as Packet Tracer/GNS3 verified until the above tests have actually been completed.**
