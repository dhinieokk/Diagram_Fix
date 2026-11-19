"""Ubah .svg menjadi .png (skala 2) dengan Chromium bawaan Playwright."""
import sys, asyncio, pathlib
from playwright.async_api import async_playwright

async def main(paths):
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(device_scale_factor=2)
        for s in paths:
            sp = pathlib.Path(s).resolve()
            await pg.goto(sp.as_uri())
            el = await pg.query_selector("svg")
            await el.screenshot(path=str(sp.with_suffix(".png")))
        await b.close()

asyncio.run(main(sys.argv[1:]))
