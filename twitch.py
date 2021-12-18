import asyncio
import logging
from flask import Blueprint, jsonify
from pyslobs import connection, ScenesService, StreamingService, ConnectionConfig

logging.basicConfig(level=logging.DEBUG)

bp = Blueprint('twitch', __name__, url_prefix='/twitch')


@bp.get("/scene/<string:name>")
async def scene(name):
    print("Calling scene():", name)
    await change_scene(name)
    print("returning true")
    return jsonify(success=True)


@bp.get("/toggle_streaming")
async def toggle_streaming():
    print("Calling toggle_streaming()")
    await go_toggle_streaming()
    return jsonify(success=True)


@bp.get("/toggle_recording")
async def toggle_recording():
    print("Calling toggle_recording()")
    await go_toggle_recording()
    return jsonify(success=True)


async def change_scene(name):
    print("Calling toggle_scene()", name)
    # Note: This assumes an INI file has been configured.
    conn = connection.SlobsConnection(ConnectionConfig("b1248f338a7f41d39714ca5b22a063eb68448c"))

    # Give CPU to both your task and the connection instance.
    await asyncio.gather(
        conn.background_processing(),
        # do_your_thing(conn)
        toggle_scene(conn, name)
    )


async def go_toggle_streaming():
    print("Calling go_toggle_streaming()")
    # Note: This assumes an INI file has been configured.
    conn = connection.SlobsConnection(ConnectionConfig("b1248f338a7f41d39714ca5b22a063eb68448c"))

    # Give CPU to both your task and the connection instance.
    await asyncio.gather(
        conn.background_processing(),
        # do_your_thing(conn)
        toggle_streaming(conn)
    )


async def go_toggle_recording():
    print("Calling go_toggle_recording()")
    # Note: This assumes an INI file has been configured.
    conn = connection.SlobsConnection(ConnectionConfig("b1248f338a7f41d39714ca5b22a063eb68448c"))

    # Give CPU to both your task and the connection instance.
    await asyncio.gather(
        conn.background_processing(),
        toggle_recording(conn)
    )
async def toggle_scene(conn, scene):
    print("Calling toggle_scene() with scene:", scene)
    try:
        completed_event = asyncio.Event()
        sc = SceneControl(conn, completed_event)
        # await sc.toggle_scene(conn, scene)
        await sc.toggle_scene(conn, scene)
        await completed_event.wait()
    except Exception:
        logging.exception("Unexpected exception")
    finally:
        await conn.close()


async def toggle_streaming(conn):
    print("Calling toggle_stream()")
    try:
        completed_event = asyncio.Event()
        sc = StreamControl(conn, completed_event)
        await sc.toggle_streaming(conn)
        await completed_event.wait()
    except Exception:
        logging.exception("Unexpected exception")
    finally:
        await conn.close()


async def toggle_recording(conn):
    print("Calling toggle_recording()")
    try:
        completed_event = asyncio.Event()
        sc = StreamControl(conn, completed_event)
        await sc.toggle_recording(conn)
        await completed_event.wait()
    except Exception:
        logging.exception("Unexpected exception")
    finally:
        await conn.close()


class SceneControl:
    def __init__(self, conn, completed_event):
        print("__init__")
        self._started = False
        self._ss = ScenesService(conn)
        self._completed_event = completed_event

    async def start(self):
        print("calling start()")
        self._started = True

    def _dump_stats(self):
        print("self._started:", self._started)
        print("----")

    async def toggle_scene(self, conn, name):
        print("calling toggle_scene:", name)
        self._started = True
        scenes = await self._ss.get_scenes()
        for scene in scenes:
            print(" - ", scene.name)
            if scene.name == name:
                await self._ss.make_scene_active(scene.id)
        self._dump_stats()


class StreamControl:
    def __init__(self, conn, completed_event):
        print("__init__")
        self._started = False
        self._ss = StreamingService(conn)
        self._completed_event = completed_event

    async def start(self):
        print("calling start()")
        self._started = True

    def _dump_stats(self):
        print("self._started:", self._started)
        print("----")

    async def toggle_streaming(self, conn):
        print("calling toggle_streaming")
        await self._ss.toggle_streaming()
        self._dump_stats()

    async def toggle_recording(self, conn):
        print("calling toggle_recording")
        await self._ss.toggle_recording()
        self._dump_stats()
