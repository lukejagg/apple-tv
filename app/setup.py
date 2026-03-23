"""Interactive setup — discover, pair, and configure Apple TV."""
import asyncio
import json
import subprocess
import sys

import pyatv
from pyatv.const import Protocol

from .config import (
    CONFIG_DIR, CONFIG_FILE, CREDS_FILE, load_config, save_config, save_credentials,
)


async def discover():
    """Discover Apple TVs on the local network."""
    loop = asyncio.get_event_loop()
    print("Scanning for Apple TVs...")
    devs = await pyatv.scan(loop, timeout=5)
    if not devs:
        print("No Apple TVs found. Make sure your Apple TV is on and on the same network.")
        return None
    if len(devs) == 1:
        d = devs[0]
        print(f"Found: {d.name} at {d.address}")
        return d
    for i, d in enumerate(devs):
        print(f"  [{i+1}] {d.name} ({d.address})")
    choice = input(f"Select [1-{len(devs)}]: ").strip()
    return devs[int(choice) - 1]


async def pair_pyatv(ip: str):
    """Pair pyatv for remote control (Companion + AirPlay)."""
    loop = asyncio.get_event_loop()
    devs = await pyatv.scan(loop, hosts=[ip], timeout=5)
    if not devs:
        print(f"Apple TV not found at {ip}")
        return {}

    conf = devs[0]
    creds = {}
    for proto in [Protocol.Companion, Protocol.AirPlay]:
        print(f"\n--- Pairing {proto.name} ---")
        pairing = await pyatv.pair(conf, proto, loop)
        await pairing.begin()
        pin = input(f"Enter PIN shown on Apple TV for {proto.name}: ")
        pairing.pin(int(pin))
        await pairing.finish()
        if pairing.service.credentials:
            creds[proto.name] = pairing.service.credentials
            print(f"  Paired!")
        await pairing.close()
    return creds


async def pair_pmd3(ip: str):
    """Pair pymobiledevice3 for screenshots."""
    # Discover the manual-pairing service
    print("\nLooking for pymobiledevice3 pairing service...")
    print("Make sure Apple TV is on: Settings > Remotes and Devices > Remote App and Devices")
    input("Press Enter when ready...")

    # Use dns-sd to find the manual pairing port
    proc = subprocess.Popen(
        ["dns-sd", "-B", "_remotepairing-manual-pairing._tcp", "local"],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
    )
    import time
    time.sleep(4)
    proc.kill()
    output = proc.stdout.read()

    # Find the instance name
    instance_name = None
    for line in output.splitlines():
        if "Add" in line and "local." in line:
            parts = line.split()
            instance_name = " ".join(parts[6:])
            break

    if not instance_name:
        print("Could not find Apple TV manual pairing service.")
        print("Make sure Developer Mode is enabled and you're on the Remote App and Devices screen.")
        return None, None

    # Resolve the service
    proc = subprocess.Popen(
        ["dns-sd", "-L", instance_name, "_remotepairing-manual-pairing._tcp", "local"],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
    )
    time.sleep(3)
    proc.kill()
    output = proc.stdout.read()

    port = None
    identifier = None
    for line in output.splitlines():
        if "can be reached at" in line:
            # Extract port
            parts = line.split(":")
            for p in parts:
                try:
                    port = int(p.split()[0])
                except (ValueError, IndexError):
                    continue
        if "identifier=" in line:
            for part in line.split():
                if part.startswith("identifier="):
                    identifier = part.split("=", 1)[1]

    if not port or not identifier:
        print("Could not resolve pairing service details.")
        return None, None

    print(f"Found pairing service: {identifier} on port {port}")

    # Do the pairing
    from pymobiledevice3.remote.tunnel_service import RemotePairingManualPairingService
    async with RemotePairingManualPairingService(identifier, ip, port) as service:
        await service.connect(autopair=True)
        print("pymobiledevice3 paired!")

    return identifier, port


async def run_setup():
    """Full interactive setup."""
    print("=== Apple TV Setup ===\n")

    # Step 1: Discover
    dev = await discover()
    if not dev:
        return

    ip = str(dev.address)
    name = dev.name
    cfg = load_config()
    cfg["ip"] = ip
    cfg["name"] = name

    # Step 2: Pair pyatv
    print("\n--- Step 1: Pair remote control (pyatv) ---")
    creds = await pair_pyatv(ip)
    if creds:
        save_credentials(creds)
        print("Credentials saved.")

    # Step 3: Pair pymobiledevice3 (for screenshots)
    print("\n--- Step 2: Pair screenshots (pymobiledevice3) ---")
    print("This requires Developer Mode on Apple TV.")
    print("Enable it: Settings > Privacy & Security > Developer Mode > ON")
    do_pmd3 = input("Pair for screenshots? [Y/n]: ").strip().lower()
    if do_pmd3 != "n":
        pairing_id, _ = await pair_pmd3(ip)
        if pairing_id:
            cfg["pmd3_pairing_id"] = pairing_id

    save_config(cfg)
    print(f"\nConfig saved to {CONFIG_FILE}")
    print(f"\nSetup complete! Run 'apple-tv install' to set up the background services.")
