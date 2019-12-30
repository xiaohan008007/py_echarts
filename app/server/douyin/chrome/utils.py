import asyncio
from pyppeteer import connect


async def sign_(wsid,tac,user_id):
    browser = await connect(browserWSEndpoint=wsid)
    # browser.goto('http://www.baidu.com')
    pages = await browser.pages()

    page = pages[0]
    # await page.screenshot({
    #
    #     path: 'baidu_iphone_X_search_puppeteer.png'
    #
    # })
    # page.goto('http://www.baidu.com')
    # await page.goto('http://wwww.baidu.com')
    # title = await page.title()
    # print("=======:"+title)
    await page.setUserAgent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36")
    sign = await page.evaluate('generateSignature', tac, user_id)
    return sign


def gen(wsid,tac,user_id):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    sign = loop.run_until_complete(sign_(wsid,tac,user_id))
    return sign


if __name__ == '__main__':
    pass