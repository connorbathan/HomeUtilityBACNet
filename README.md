# HomeUtilityBACNet

A self-hosted BACnet/IP gateway for residential utility usage. The first milestone serves simulated water points for Siemens commissioning. Every sample point has a `SIMULATED` description, and `WTR_DATA_VALID` stays inactive. Live AquaHawk retrieval, SQLite history, SCE, and SoCalGas are future milestones.

## Debian 13 installation

Run as root in the Proxmox LXC. Replace the example IP address and prefix with the address on the container's BACnet interface. Keep UDP 47808 on the private network.

```bash
(
set -eu
apt-get update
apt-get install -y git python3-venv ca-certificates
git clone https://github.com/connorbathan/HomeUtilityBACNet.git /opt/home-utilities
cd /opt/home-utilities
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m unittest discover -s tests -v
install -d -m 0755 /etc/home-utilities
install -m 0644 deploy/gateway.env.example /etc/home-utilities/gateway.env
sed -i 's|^BACNET_ADDRESS=.*|BACNET_ADDRESS=192.0.2.10/24:47808|' /etc/home-utilities/gateway.env
install -m 0644 deploy/home-utilities.service /etc/systemd/system/home-utilities.service
systemctl daemon-reload
systemctl enable --now home-utilities
)
```

The installation uses an empty `/opt/home-utilities` path. For local tests without systemd, run `python -m home_utilities.server` from the repository with the dependencies installed. That binds to loopback by default.

## Commissioning

- Run `systemctl status home-utilities --no-pager`, `journalctl -u home-utilities -b -n 40 --no-pager`, and `ss -lun 'sport = :47808'` on the CT.
- From Siemens, discover device instance `6012`, name `HOME_UTILITIES`. Use a BACnet/IP broadcast on the same subnet or directed discovery if your client supports it.
- Read `AV:1` (`WTR_LAST_HOUR`) and verify its present value is 12 US gallons. Read `BV:3` (`WTR_DATA_VALID`) and verify it is inactive.
- `WriteProperty` and `WritePropertyMultiple` are denied. A write attempt on a simulated point should return `writeAccessDenied`.

## Water points

The water allocation is AV:1-19. AV:1-11 and BV:1-3 are defined in [points.py](home_utilities/points.py). AV:6 `WTR_CCF_MONTH` exposes standard BACnet cubic feet. Divide by 100 when displaying CCF in Siemens. `WTR_AVG_GPM` is an average over reported hourly intervals, with standard US gallons per minute units.
