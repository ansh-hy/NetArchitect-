# NetArchitect User Guide

## Start the application

```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

## Use a preset
1. Select **Preset scenario** in the sidebar.
2. Choose Campus LAN, Metro MAN or Global WAN.
3. Select **Analyze network**.
4. Review Overview, Architecture, IP Addressing, Decision Rationale, Cisco Configurations and Validation.
5. Download subnet CSV or the generated config/report ZIP.

## Use a custom scenario
1. Select **Custom scenario**.
2. Enter the scenario profile and network parameters.
3. Enter subnet requirements one per line as `NAME,HOSTS`.
4. Enter VLAN requirements one per line as `ID,NAME,PURPOSE`.
5. Enter a canonical IPv4 root network such as `10.40.0.0/16`.
6. Select **Analyze network** and resolve any validation messages.

## Interpret generated artifacts
- `switches.cfg`: VLAN and trunk baseline; check actual device interface inventory.
- `svis.cfg`: SVI gateways and, for single-area Campus OSPF, OSPF on the Layer 3 gateway switch.
- `routers.cfg`: edge router baseline and explicit missing-input notes.
- `acls.cfg`: security policy placeholder; no broad ACL is guessed.
- `vpn.cfg`: IPsec deployment-input checklist; peer/crypto values are not invented.
- `route_summarization.cfg`: explains missing per-site aggregates before safe summary commands can be emitted.
- `vlsm_allocations.csv`: calculated subnet ranges, masks, gateway and utilization.
- `decision_report.json`: machine-readable rationale and assumptions.

## Engineering safety
Review all configuration text against the target hardware and IOS version. Never paste generated config into a production device without review, backup, change approval and lab validation.
