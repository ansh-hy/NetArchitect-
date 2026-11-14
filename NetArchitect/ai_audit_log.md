# AI Audit Log — NetArchitect (CIC-307)

**Purpose:** Record concrete AI-assisted implementation defects, their technical diagnosis, remediation and packet-flow implications, as required by the assignment's AI Defense & Code Auditing Log.

**Integrity note:** The examples below are defects found in intermediate AI-generated project code during this development. The prompts are concise reconstructions of the implementation requests, not claimed verbatim chat transcripts. The buggy snippets are representative of the actual intermediate implementation. The final repository contains the remediations and regression tests.

---

## Audit case 1 — Incorrectly placing every multi-area OSPF network in Area 0

### Prompt / task context
"Generate the router configuration template for the routing recommendation, including the Multi-Area OSPF case."

### Intermediate AI-generated buggy code
```jinja2
{% elif routing.protocol.startswith("Multi-Area OSPF") %}
router ospf 1
 router-id 1.1.1.1
{% for subnet in subnets %}
 network {{ subnet.network_address }} {{ subnet.wildcard_mask }} area 0
{% endfor %}
```

### Technical diagnosis
The decision engine selected Multi-Area OSPF, but the template placed every subnet into Area 0. That is not a multi-area design: there is no non-backbone area, no Area Border Router (ABR), and no subnet-to-area assignment. The generated configuration contradicted the selected architecture and could mislead an operator into believing that routing-domain isolation had been implemented.

### Packet-flow analysis
For a host in a remote-site subnet to reach a host in the headquarters subnet, the packet would first use its local default gateway. The gateway would consult its routing table for the remote prefix. In a real multi-area OSPF design, the relevant area routes are exchanged through an ABR and the backbone (Area 0), subject to the area topology and route policy. The buggy configuration instead advertised all networks as Area 0, so it did not create the intended area boundary or ABR behavior. A ping might still work in a flat single-area lab, but that would not validate the required multi-area architecture.

### Remediation
The final template does **not** fabricate an area map. It explicitly withholds Multi-Area OSPF commands until the subnet-to-area mapping, ABR placement, router IDs and routed interfaces are provided. It includes a regression test that ensures a multi-area recommendation is not silently rendered as Area 0.

**Final behavior:** recommendation is explainable; deployment configuration is withheld where required design inputs are absent.

---

## Audit case 2 — Overly permissive management ACL

### Prompt / task context
"Generate an ACL configuration template for the management VLAN."

### Intermediate AI-generated buggy code
```jinja2
ip access-list extended NETARCHITECT-MGMT-ONLY
 permit ip {{ management_subnet.network_address }} {{ management_subnet.wildcard_mask }} any
 deny ip any any log
```

### Technical diagnosis
The rule permitted **all IP protocols** from every host in the management subnet to **any destination**. The ACL name implied management-only access, but the rule did not restrict destinations, protocols or management services. This violates least-privilege design and could allow management hosts to initiate unrelated traffic. The scenario input did not include an approved destination list or service policy, so a safe ACL could not be inferred.

### Packet-flow analysis
For a packet sourced from the management subnet, the first ACE matched all IP traffic and any destination, so the packet was permitted. The later deny statement was never reached for that source/destination pair. Therefore, the policy was broader than the label suggested. A meaningful validation would test allowed management traffic to approved device addresses and denied management traffic to unapproved destinations/services; those policy values are not supplied in the assignment presets.

### Remediation
The final ACL template emits a clearly marked policy placeholder and **does not emit any permit statement** until explicit source, destination and service requirements are supplied. It is not automatically applied to an interface. A regression test checks that `permit ip` is absent.

**Final behavior:** no guessed security policy is generated.

---

## Additional hardening — Non-finite physical distance

The initial distance engine rejected negative values but did not explicitly reject IEEE-754 `NaN` or infinity. A `NaN` comparison can be false for both `<` and `<=` tests and could fall through to an unintended media branch. The final engine checks `math.isfinite()` in both media selection and copper validation. Regression tests cover NaN and positive/negative infinity.

---

## Audit conclusion

The audit demonstrates why AI-generated network code must be reviewed against protocol behavior and packet flow rather than accepted because it compiles. The final code favors explicit configuration withholding over inventing OSPF areas, BGP peer parameters or security policy. Regression tests preserve the corrected behavior.

**Simulator evidence status:** No Packet Tracer/GNS3 packet capture or `.pkt`/`.gns3` project is claimed by this repository build. Use the supplied simulator verification plan to produce that evidence on the installed simulator and target device models.
