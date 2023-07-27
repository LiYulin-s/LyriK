from pycloudmusic import Music163Api
from typing import Generator
from pycloudmusic.object.music163 import Music, Album
import asyncio


async def main():
    api = Music163Api()
    g: tuple[int, Generator[Music, None, None]] = await api.search_music(
        "Weight of the World (Nouveau-FR Version) " + "NieR:Automata Original Soundtrack "+"Emi Evans " + "岡部啓一",
        0,
        30,
    )
    print(g[0])
    gen = g[1]
    for music in gen:
        print(f"{music.name_str} {music.album_data} {music.artist} {await music.lyric()}")


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
