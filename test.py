import asyncio
from time import sleep
import aiohttp

from paperless import Auth, PaperlessAPI


async def main():
    async with aiohttp.ClientSession() as session:
        auth = Auth(session, "http://nas.local.tbsch.de:9120/api",
                    "17d85e03b83c4bfd9aa0e9a4e71dc3b79265d51e")

        api = PaperlessAPI(auth)

        correspondents = await api.async_get_correspondents()
        correspondents = await api.async_get_correspondents()
        correspondents = await api.async_get_correspondents()

        for data in correspondents:
            print(data.raw_data)

        # doctypes = await api.async_get_document_types()

        # for data in doctypes:
        #     print(data.raw_data)

        # tags = await api.async_get_tags()

        # for data in tags:
        #     print(data.raw_data)

        # views = await api.async_get_saved_views()

        # for data in views:
        #     print(data.raw_data)

        # docs = await api.async_get_documents()

        # for data in docs:
        #     print(data.raw_data)


asyncio.run(main())
