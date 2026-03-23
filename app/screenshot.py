"""Take Apple TV screenshots via pymobiledevice3 developer services tunnel."""
import os
from .config import load_config, get_user_uid, get_user_gid
from .patch import ensure_buffer_patched


async def take(out_path: str | None = None) -> tuple[str | None, bytes]:
    """Take a screenshot. Returns (path, png_bytes).

    Requires root for TUN interface creation.
    """
    ensure_buffer_patched()
    from pymobiledevice3.remote.tunnel_service import RemotePairingTunnelService
    from pymobiledevice3.remote.remote_service_discovery import RemoteServiceDiscoveryService
    from pymobiledevice3.services.dvt.instruments.dvt_provider import DvtProvider
    from pymobiledevice3.services.dvt.instruments.screenshot import Screenshot

    cfg = load_config()
    pairing_id = cfg["pmd3_pairing_id"]
    ip = cfg["ip"]
    port = cfg["pmd3_tunnel_port"]

    if not pairing_id or not ip:
        raise RuntimeError("Not configured. Run: apple-tv setup")

    service = RemotePairingTunnelService(pairing_id, ip, port)
    await service.connect(autopair=False)
    async with service.start_tcp_tunnel() as tunnel:
        rsd = RemoteServiceDiscoveryService((tunnel.address, tunnel.port))
        await rsd.connect()
        async with DvtProvider(rsd) as dvt, Screenshot(dvt) as screenshot:
            data = await screenshot.get_screenshot()
        if out_path:
            os.makedirs(os.path.dirname(out_path), exist_ok=True)
            with open(out_path, "wb") as f:
                f.write(data)
            # Fix ownership if running as root
            if os.geteuid() == 0:
                os.chown(out_path, get_user_uid(), get_user_gid())
    return out_path, data
