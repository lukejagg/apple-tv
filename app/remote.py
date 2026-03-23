"""pyatv remote control — power, navigation, playback, volume."""
import asyncio
import pyatv
from pyatv.const import Protocol
from .config import load_config, load_credentials


async def connect():
    cfg = load_config()
    creds = load_credentials()
    loop = asyncio.get_event_loop()
    hosts = [cfg["ip"]] if cfg.get("ip") else []
    devs = await pyatv.scan(loop, hosts=hosts, timeout=5)
    if not devs:
        raise ConnectionError(f"Apple TV not found" + (f" at {cfg['ip']}" if cfg.get("ip") else ""))
    conf = devs[0]
    if creds.get("Companion"):
        conf.set_credentials(Protocol.Companion, creds["Companion"])
    if creds.get("AirPlay"):
        conf.set_credentials(Protocol.AirPlay, creds["AirPlay"])
    return await pyatv.connect(conf, loop)


async def send(action: str):
    atv = await connect()
    try:
        rc = atv.remote_control
        actions = {
            "up": rc.up, "down": rc.down, "left": rc.left, "right": rc.right,
            "select": rc.select, "ok": rc.select,
            "menu": rc.menu, "back": rc.menu,
            "home": rc.home, "top_menu": rc.top_menu,
            "play": rc.play, "pause": rc.pause, "playpause": rc.play_pause,
            "next": rc.next, "prev": rc.previous,
            "volume_up": rc.volume_up, "volume_down": rc.volume_down,
        }
        fn = actions.get(action)
        if fn is None:
            raise ValueError(f"Unknown action: {action}")
        await fn()
    finally:
        atv.close()


async def power(on: bool):
    atv = await connect()
    try:
        if on:
            await atv.power.turn_on()
        else:
            await atv.power.turn_off()
    finally:
        atv.close()


async def status() -> dict:
    atv = await connect()
    try:
        playing = await atv.metadata.playing()
        return {
            "power": str(atv.power.power_state),
            "state": str(playing.device_state),
            "title": playing.title,
            "artist": playing.artist,
        }
    finally:
        atv.close()
