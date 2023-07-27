from pycloudmusic.object.music163 import Music, Album

from netwrok_interface import (
    AbstractNetworkInterface,
    LyricsResponse,
    NoFoundError,
    InternetError,
)

from pycloudmusic import Music163Api

from pycloudmusic.error import Music163BadCode, CannotConnectApi, Music163BadData

from typing import Generator, Tuple, Dict, Any

import asyncio


class NeteaseMusicInterface(AbstractNetworkInterface):
    def __init__(self) -> None:
        self.__api = Music163Api()

    def name(self):
        return "NeteaseMusicInterface"

    async def get_lyrics(
        self, title: str, album: str, artist: str, hazy_search=True
    ) -> LyricsResponse:
        result: tuple[
            int, Generator[Music, None, None]
        ] = await self.__api.search_music(
            "{0} {1} {2}".format(title, album, " ".join(artist)), 0
        )
        (count, generator) = result
        music_list: list[tuple[int, Music]] = []
        for page in range(count // 30 if count % 30 == 0 else count // 30 + 1):
            try:
                result: tuple[
                    int, Generator[Music, None, None]
                ] = await self.__api.search_music(
                    "{0} {1} {2}".format(title, album, " ".join(artist)), page
                )
                for music in generator:
                    if not music.name[0] == title:
                        continue
                    if music.album_data["name"] == album and set(
                        a["name"] for a in music.artist
                    ) == set(artist):
                        lyrics = await music.lyric()
                        return LyricsResponse(
                            False,
                            lyrics["lrc"]["lyric"],
                            None
                            if lyrics["tlyric"]["lyric"] == ""
                            else {"zh_CN": lyrics["tlyric"]["lyric"]},
                        )
                    elif hazy_search:
                        weight = 0
                        if music.album_data["name"] == album:
                            weight += 1
                        if set(a["name"] for a in music.artist) == set(artist):
                            weight += 1
                        music_list.append((weight, music))
            except KeyError as exception:
                raise NoFoundError(self, title, artist, album) from exception
            except (Music163BadData, Music163BadCode, CannotConnectApi) as exception:
                raise InternetError(self) from exception
        if len(music_list) == 0:
            raise NoFoundError(self, title, artist, album)
        lyrics = await max(music_list, key=lambda x: x[0])[1].lyric()
        return LyricsResponse(
            True,
            lyrics["lrc"]["lyric"],
            None
            if lyrics["tlyric"]["lyric"] == ""
            else {"zh_CN": lyrics["tlyric"]["lyric"]},
        )


async def main():
    api = NeteaseMusicInterface()
    lyrics = await api.get_lyrics(
        "Weight of th",
        "NieR:Automata Original Soundtrack",
        ["Emi Evans", "岡部啓一"],
    )
    print(lyrics)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
