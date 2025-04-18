import os
import copy
import re
from turtle import reset
from unittest import result
import httpx
import hashlib, uuid, time, json
import requests
import asyncio
from mcp.server.fastmcp import FastMCP, Context

# APP_ID = os.getenv("APP_ID")
# APP_SECRET = os.getenv("APP_SECRET")
# OPEN_ID = os.getenv("OPEN_ID")
# IS_TEST = os.getenv("OPENAPI_URL_BASE")
# ORDER_CITY = os.getenv("ORDER_CITY")
# OPENAPI_URL_BASE = "https://api-open.uupt.com/openapi/v3/"


OPENAPI_URL_BASE = "http://api-open.test.uupt.com/openapi/v3/"
APP_ID = "ccba8bd4a2d54a2fb6df97e87979f303"
APP_SECRET = "e3424d4b31fb40dba6c32407b44e7783"
OPEN_ID = "f9fd1cdf45d645ffbd6de4877c636a84"
ORDER_CITY = "郑州市"

# 创建MCP服务器实例
mcp = FastMCP("mcp-server-uupt-orders")


@mcp.tool()
async def order_price(from_address: str,  # 开始地址，例如：阳光城5号楼6层6号
                      to_address: str,  # 结束地址，例如：楷林国际4层210号
                      city_name: str,  # 配送城市名字，如果没有带’市‘，需要补充，比如郑州市，不能只是郑州
                      # ctx: Context
                      ) -> dict:
    """
    Name:
        智能发单-订单询价

    Description:
        查询订单价格，需要需要输入开始地址，结束地址。

    Args:
        from_address: 开始地址，要求完整地址信息。必要字段
        to_address: 结束地址，要求完整地址信息，必要字段
        city_name:  配送城市名字，如果没有带’市‘，需要补充，比如郑州市，不能只是郑州,建议参数
    """
    if ORDER_CITY:
        city_name = ORDER_CITY
    biz = {
        'fromAddress': from_address,
        'toAddress': to_address,
        'sendType': "SEND",
        'cityName': city_name,
        'specialChannel': 1
    }
    url = f"{OPENAPI_URL_BASE}order/orderPrice"
    await post_send(biz, url)


@mcp.tool()
async def order_create(price_token: str,  # 计算订单价格接口返回的price_token
                       receiver_phone: str,  # 收件人电话，例如：15288888888
                       # ctx: Context
                       ) -> dict:
    """
    Name:
        智能发单-创建订单
        
    Description:
        自动创建订单，需要需要输入：
        计算订单价格接口返回的price_token，必传字段
        收件人电话。receiver_phone,必传字段
        
    Args:
        price_token: 计算订单价格接口返回的price_token
        receiver_phone: 收件人联系电话
    """

    biz = {
        'priceToken': price_token,
        'receiver_phone': receiver_phone,
        'pushType': "OPEN_ORDER",
        'payType': "BALANCE_PAY",
        'specialChannel': 1,
        'specialType': "NOT_NEED_WARM"
    }
    url = f"{OPENAPI_URL_BASE}order/addOrder"
    await post_send(biz, url)


@mcp.tool()
async def order_query(order_code: str,  # 订单编号order_code
                      # ctx: Context,
                      ) -> dict:
    """
    Name:
        智能发单-获取订单详情
        
    Description:
        获取订单详情，需要需要输入订单编号：
        订单编号order_code
    Args:
        order_code: 订单编号order_code
    """
    biz = {
        'order_code': order_code
    }

    url = f"{OPENAPI_URL_BASE}order/orderDetail"
    await post_send(biz, url)


@mcp.tool()
async def order_cancel(order_code: str,  # 订单编号order_code
                       reason: str,  # 取消原因reason，例如：不想取了
                       # ctx: Context,
                       ) -> dict:
    """
    Name:
        智能发单-取消订单

    Description:
        取消订单，需要需要输入订单编号：
        订单编号order_code
        取消原因reason

    Args:
        order_code: 订单编号order_code
        reason: 取消原因reason
   """
    biz = {
        'order_code': order_code,
        'reason': reason
    }
    url = f"{OPENAPI_URL_BASE}order/cancelOrder"
    await post_send(biz, url)


@mcp.tool()
async def driver_track(order_code: str,  # 订单编号order_code
                       # ctx: Context,
                       ) -> dict:
    """
    Name:
        智能发单-跑男信息查询,查询跑腿实时信息

    Description:
        跑男信息查询，需要需要输入订单编号：
        订单编号order_code

    Args:
        order_code: 订单编号order_code
   """
    biz = {
        'order_code': order_code,
    }
    url = f"{OPENAPI_URL_BASE}order/driverTrack"
    await post_send(biz, url)


async def post_send(biz, url):
    timestamp = int(time.time())
    sign_str = json.dumps(biz, ensure_ascii=False, indent=4) + APP_SECRET + str(timestamp)
    sign = hashlib.md5(sign_str.encode(encoding='UTF-8')).hexdigest().upper()
    payload = {
        'openId': OPEN_ID,
        'timestamp': timestamp,
        'biz': json.dumps(biz, ensure_ascii=False, indent=4),
        'sign': sign
    }
    print(f"请求参数: {json.dumps(payload, ensure_ascii=False, indent=4)}")
    headers = {
        "X-App-Id": "9200a7a447234076843b2e0fbfc4f5fc",  # appid
        "Content-Type": "application/json"
    }
    try:
        print("请求URL: ", url)
        res = requests.post(url, json=payload, headers=headers)
        if res.status_code == 200:
            print("result: ", res.json())
            return res.json()
        else:
            print(f"Error: {res.status_code}, {res.text}")
        return '错误'
    except requests.RequestException as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    # mcp.run()
    # asyncio.run(order_price("阳光城", "楷林国际", "郑州市"))
     asyncio.run(order_create("2ae61aa991124198b2f4a2b5a3f8087f", "18888888888"))
    # asyncio.run(order_query("250417180110028000037930"))
