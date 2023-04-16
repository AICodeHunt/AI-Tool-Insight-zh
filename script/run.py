import json
import logging
from io import StringIO
from tornado.httpclient import AsyncHTTPClient, HTTPRequest
from tornado.ioloop import IOLoop
from pyquery import PyQuery



"""
https://www.futurepedia.io/api/tools?page=2&sort=new
"""


async def get_tools_by_page(page, sort="new"):
    try:
        url = 'https://www.futurepedia.io/api/tools?page={}&sort={}'.format(page, sort)
        response = await AsyncHTTPClient().fetch(HTTPRequest(url))
        return json.loads(response.body.decode())
    except Exception as e:
        logging.exception(e)
        return []


"""
https://www.futurepedia.io/api/getPosts?page=1&sort=New&time=Today
"""


async def get_recent(*args, **kwargs):
    try:
        url = 'https://www.futurepedia.io/recent'
        response = await AsyncHTTPClient().fetch(HTTPRequest(url))
        query = PyQuery(response.body.decode())
        script_content = query('#__NEXT_DATA__').text()
        # return json.loads(script_content)['props']['pageProps']['todayTools']
        for item in json.loads(script_content)['props']['pageProps']['todayTools']:
            yield item
    except Exception as e:
        logging.exception(e)
        # return []


def format_tool(item):
    try:
        ref = item['mainImage'].get('asset', {}).get('_ref', '').split('-')
        image = 'https://cdn.sanity.io/images/u0v1th4q/production/{}-{}.{}?w=640&h=334&auto=format&q=75'.format(ref[1], ref[2], ref[3])
    except Exception as e:
        logging.error(e)
        image = ''

    price = item.get('startingPrice', '')
    return '|{} |{} |{} |{} |{} |{} |'.format(
        item['toolName'].replace('|', ' '),
        item['toolShortDescription'].replace('|', ' '),
        '[{}]({})'.format('visit website', item['websiteUrl']),
        '![]({})'.format(image) if image else '',
        '$ {}'.format(price) if price else '',
        # ' '.join(['`{}`'.format(p) for p in item['pricing']]),
        ' '.join(['`{}`'.format(c['categoryName']) for c in item['toolCategories']]),
    )


async def get_all_content(executor):
    page = 1
    res = []
    while page > 0:
        result = await executor(page)
        if len(result) == 0:
            logging.info("no more tools %r", page)
            page = -1
        else:
            page = page + 1

        # test
        # page = -1
        for item in result:
            res.append(item)
            yield item
    json.dump(res, open('tools.json', 'w+'))


async def main():
    print("""# AI-Tool-Insight
AI Tool Insight 旨在为大家提供最新 AI 资讯，助力创造未来无限可能
每日更新，欢迎大家每天来看看又有什么新的好玩的AI工具  
网站：https://www.aitoolinsight.com
## 🏠微信 & 知识星球
加入社群，与AI技术领域的专家和爱好者一起探讨最前沿的信息！在这里，你可以体验到最先进的人工智能技术，与志同道合的人交流，共同提升你的知识水平。不管你是专业人士还是爱好者，都欢迎加入我们的群体！  
<div style="display: flex;">
<img src="https://user-images.githubusercontent.com/1826685/232313468-cd46d9bc-35ad-4242-a7b4-99a6cc58d2d2.png" width="49%" style="flex: 1" />
<img src="https://user-images.githubusercontent.com/1826685/232313476-665c63de-8680-4bd3-a571-34cc03724083.png" width="49%"  style="flex: 1" />
</div>

## 🔥今日更新
| 工具名称 | 工具描述| 网站链接 | 网站截图 | 工具价格 | 分类 |
|---|---|---|---|---|---|""")
    async for item in get_recent():
        # print(item['_id'], item['title'])
        print(format_tool(item))

    # print('--------------')
    print("""
## 📖全部工具
| 工具名称 | 工具描述| 网站链接 | 网站截图 | 工具价格 | 分类 |
|---|---|---|---|---|---|""")
    async for item in get_all_content(get_tools_by_page):
        # print(item['_id'], item['toolName'])
        print(format_tool(item))


if __name__ == "__main__":
    IOLoop.current().run_sync(main)


