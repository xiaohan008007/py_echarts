import asyncio
from pyppeteer import launch
from pyquery import PyQuery as pq


async def main():
    browser = await launch()
    page = await browser.newPage()
    await page.goto('http://quotes.toscrape.com/js/')
    html = await page.content()
    #print(html)
    doc = pq(html)
    print('Quotes:', doc('.quote').length)
    its = doc('.container .quote').items()
    for it in its:
        print(it)
        it1 = it("span:nth-child(1)")
        print(it1.text())
        print(it1.attr('class'))
        break
    await browser.close()


asyncio.get_event_loop().run_until_complete(main())