# NetArchitect — Explainable Network Recommendation & Configuration Engine

**Course:** CIC-307 — Computer Networks Mini-Project  
**Project:** NetArchitect  
**Status:** Integrated software project (Phases 1–8); simulator verification must be completed and evidenced by the project team.

## 1. Project overview

NetArchitect is a Python-based network planning and Cisco configuration recommendation application. It accepts predefined or custom network requirements, evaluates network design choices, calculates IPv4 subnet allocations, recommends topology and routing approaches, generates Cisco IOS configuration baselines, and explains the engineering reasoning behind its recommendations.

The central feature is its **Explainable Decision Engine**: recommendations are accompanied by the input assumptions, technical rationale, relevant calculations, and limitations rather than being presented as unexplained output.

## 2. Main capabilities

- **Scenario input:** Campus LAN, Metro MAN, Global WAN presets, and custom scenario input with validation.
- **Physical media planning:** Recommends media based on the assignment's distance bands and flags copper links that exceed the specified distance limit.
- **VLAN and topology planning:** Produces VLAN plans and hierarchical topology recommendations.
- **Redundancy planning:** Identifies redundancy and failover design considerations.
- **VLSM subnet allocation:** Allocates IPv4 subnets largest-first and reports network address, prefix, subnet mask, wildcard mask, usable range, gateway, broadcast address, and utilization-related details where available.
- **Routing recommendations:** Evaluates OSPF Area 0, Multi-Area OSPF, and eBGP decision cases, while identifying missing inputs where a complete design cannot safely be produced.
- **Explainable decisions:** Produces a decision report with rationale, assumptions, and limitations.
- **Cisco IOS artifacts:** Generates switch, SVI, router, ACL, VPN-planning, and route-summarization configuration artifacts as applicable.
- **Quality checks:** Includes automated tests, release verification, and an AI audit log documenting defects, diagnosis, remediation, and regression protection.

## 3. Assignment scenarios

The project includes three preset scenarios based on the CIC-307 assignment:

| Preset | Scenario summary |
|---|---|
| `campus_lan` | Three-building campus LAN, VLAN segmentation, media selection, redundancy, and single-area OSPF planning |
| `metro_man` | HQ and remote-site MAN planning, long-distance media, service/QoS and failover considerations |
| `global_wan` | Multi-city and cloud WAN planning, VPN/routing considerations, and route summarization |

Preset inputs are stored in `config/`. Generated reports and configuration artifacts are stored in `exports/`.

## 4. Technology stack

- Python 3.10+
- Streamlit
- Pydantic
- Jinja2
- pytest

Install the dependencies from `requirements.txt`.

## 5. Setup and run

### Windows (PowerShell)

```powershell
cd NetArchitect
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

### macOS / Linux

```bash
cd NetArchitect
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

Streamlit will print a local URL (usually `http://localhost:8501`) to open in your browser.

## 6. Run tests and release checks

From the project root, with the virtual environment activated:

```bash
pytest -v
python scripts/verify_release.py
python -m compileall -q app.py core generators scripts tests
```

The test suite checks core calculation and recommendation behavior, assignment boundaries, configuration generation, and release safety. Run these commands on the machine used for submission and retain genuine terminal output or screenshots as evidence.

## 7. Repository structure

```text
NetArchitect/
├── app.py
├── requirements.txt
├── README.md
├── ARCHITECTURE.md
├── USER_GUIDE.md
├── TESTING_AND_VERIFICATION.md
├── PACKET_TRACER_GNS3_GUIDE.md
├── TRACEABILITY_MATRIX.md
├── FINAL_SUBMISSION_CHECKLIST.md
├── FINAL_QA_REPORT.md
├── PROJECT_STATUS.md
├── RELEASE_NOTES.md
├── ai_audit_log.md
├── config/
│   ├── campus_lan.json
│   ├── metro_man.json
│   └── global_wan.json
├── core/
├── generators/
├── templates/
├── tests/
├── scripts/
├── exports/
│   ├── campus_lan/
│   ├── metro_man/
│   └── global_wan/
├── reference/
│   └── NetArchitect_Assignment_Specification_CIC-307.pdf
└── verification/
    └── simulator_results_template.md
```

The export folders contain generated configuration files, VLSM allocation outputs, decision reports, and a notice that simulator verification is still required.

## 8. Cisco Packet Tracer / GNS3 validation

The generated `.cfg` files are **reviewable configuration baselines**, not proof of a fully deployed or simulator-validated network. Before claiming successful simulation:

1. Build the topology using the device models available in Packet Tracer or GNS3.
2. Map the generated interface examples to the actual interfaces in your topology.
3. Review and adapt commands for the selected device model and IOS image.
4. Apply the configurations in a controlled order.
5. Verify VLANs, trunks, SVI status, inter-VLAN connectivity, routing, and redundancy.
6. Save the native simulator project (`.pkt` for Packet Tracer, or the relevant GNS3 project files).
7. Capture genuine screenshots and CLI outputs.
8. Record actual outcomes in `verification/simulator_results_template.md` (or a completed copy of it).

Do not report a test as passed unless it was actually executed and observed. Do not use an illustrative topology image as a substitute for a screenshot from the simulator.

See `PACKET_TRACER_GNS3_GUIDE.md` for the detailed procedure.

## 9. Important assumptions and limitations

- Some assignment inputs do not specify device models, IOS versions, physical interface inventories, exact OSPF area mappings, BGP peer details, or a complete security/ACL policy.
- Where required inputs are missing, the application intentionally emits a baseline, planning artifact, warning, or placeholder rather than inventing production settings.
- Review generated configurations before applying them. Interface names and supported commands vary by device.
- Carrier diversity, optical link budgets, real-world failover, VPN interoperability, and production security policy require environment-specific engineering validation.
- Packet Tracer/GNS3 execution is an external manual validation step and is not implied by passing the Python test suite.

## 10. AI audit and explainability

`ai_audit_log.md` records concrete defects identified during development, explains why they were problematic, documents the remediation, and links the fixes to regression tests. Review this file before the project demonstration so that you can explain the design decisions and the audit process.

## 11. Project documentation

| File | Purpose |
|---|---|
| `ARCHITECTURE.md` | Application architecture and component responsibilities |
| `USER_GUIDE.md` | How to use the application |
| `TESTING_AND_VERIFICATION.md` | Automated test and verification approach |
| `PACKET_TRACER_GNS3_GUIDE.md` | Simulator build and validation procedure |
| `TRACEABILITY_MATRIX.md` | Assignment requirement-to-implementation mapping |
| `ai_audit_log.md` | AI/code audit findings and fixes |
| `FINAL_QA_REPORT.md` | QA summary and verification status |
| `FINAL_SUBMISSION_CHECKLIST.md` | Remaining submission tasks |
| `PROJECT_STATUS.md` | Integrated scope and outstanding external validation |
| `RELEASE_NOTES.md` | Release summary |

## 12. Academic submission checklist

Before submitting, confirm that you have:

- [ ] Uploaded the complete source repository, including `core/`, `generators/`, `templates/`, `config/`, `tests/`, `scripts/`, and `exports/`.
- [ ] Included this README and the other project documentation.
- [ ] Included the assignment specification PDF if permitted by your course/instructor.
- [ ] Run the automated tests and release verification locally; saved genuine evidence.
- [ ] Opened the application and captured screenshots of the three presets and explainable recommendations.
- [ ] Built and saved the required Packet Tracer/GNS3 project(s), if required by the assignment.
- [ ] Captured genuine simulator topology and verification screenshots.
- [ ] Completed the simulator results record with actual test outputs.
- [ ] Added required student/team details to the report or submission form (not to public files unless appropriate).
- [ ] Checked the instructor's submission instructions for required report format, repository visibility, and naming conventions.

---

**NetArchitect — CIC-307 Computer Networks Mini-Project**  
For academic demonstration and review. Generated network configurations must be validated against the target simulator/device environment before deployment.
