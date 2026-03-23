"""Re-discover Apple TV IP on the network."""
import asyncio
import pyatv
from .config import load_config, save_config


async def run():
    cfg = load_config()
    name = cfg.get("name")
    loop = asyncio.get_event_loop()

    print(f"Scanning for Apple TVs...")
    devs = await pyatv.scan(loop, timeout=5)

    # Fallback: try existing IP directly
    if not devs and cfg.get("ip"):
        print(f"Broadcast scan empty, trying {cfg['ip']} directly...")
        devs = await pyatv.scan(loop, hosts=[cfg["ip"]], timeout=5)

    if not devs:
        print("No Apple TVs found. Make sure it's on and on the same network.")
        return

    # Try to match by name
    target = None
    if name:
        for d in devs:
            if d.name == name:
                target = d
                break

    if not target:
        if len(devs) == 1:
            target = devs[0]
        else:
            for i, d in enumerate(devs):
                print(f"  [{i+1}] {d.name} ({d.address})")
            choice = input(f"Select [1-{len(devs)}]: ").strip()
            target = devs[int(choice) - 1]

    old_ip = cfg.get("ip")
    new_ip = str(target.address)
    cfg["ip"] = new_ip
    cfg["name"] = target.name
    save_config(cfg)

    if old_ip != new_ip:
        print(f"Updated: {old_ip} → {new_ip} ({target.name})")
    else:
        print(f"IP unchanged: {new_ip} ({target.name})")
