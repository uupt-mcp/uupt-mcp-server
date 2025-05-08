import os
import copy
import re
from turtle import reset
from unittest import result
import httpx
import hashlib, uuid, time, json
import requests
import asyncio
from pydantic import Field
from mcp.server.fastmcp import FastMCP, Context

APP_ID = os.getenv("APP_ID")
APP_SECRET = os.getenv("APP_SECRET")
OPEN_ID = os.getenv("OPEN_ID")
ORDER_CITY = os.getenv("ORDER_CITY")
OPENAPI_URL_BASE = "https://api-open.uupt.com/openapi/v3/"

# 创建MCP服务器实例
mcp = FastMCP("mcp-server-uupt-orders")


@mcp.tool(name="智能发单-订单询价", description="查询订单价格，需要需要输入开始地址，结束地址。")
async def order_price(from_address: str = Field(description="开始地址，要求完整地址信息。必要字段"),  # 开始地址，例如：阳光城5号楼6层6号
                      to_address: str = Field(description="结束地址，要求完整地址信息，必要字段"),  # 结束地址，例如：楷林国际4层210号
                      city_name: str = Field(
                          description="配送城市名字，如果没有带’市‘，需要补充，比如郑州市，不能只是郑州,非必填"), ) -> dict:
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
    return post_send(biz, url)


@mcp.tool(name="智能发单-创建订单",
          description="自动创建订单，需要需要输入：计算订单价格接口返回的price_token，必传字段,收件人电话:receiver_phone,必传字段")
async def order_create(price_token: str = Field(description="计算订单价格接口返回的price_token,必填字段"),
                       receiver_phone: str = Field(description="收件人电话，例如：15288888888，必填字段"),
                       ) -> dict:
    biz = {
        'priceToken': price_token,
        'receiver_phone': receiver_phone,
        'pushType': "OPEN_ORDER",
        'payType': "BALANCE_PAY",
        'specialChannel': 1,
        'specialType': "NOT_NEED_WARM"
    }
    url = f"{OPENAPI_URL_BASE}order/addOrder"
    return post_send(biz, url)


@mcp.tool(name="智能发单-获取订单详情", description="获取订单详情，需要需要输入订单编号：订单编号order_code")
async def order_query(order_code: str = Field(description="order_code: 订单编号order_code"),
                      ) -> dict:
    biz = {
        'order_code': order_code
    }

    url = f"{OPENAPI_URL_BASE}order/orderDetail"
    return post_send(biz, url)


@mcp.tool(name="智能发单-取消订单", description="取消订单，需要需要输入订单编号")
async def order_cancel(order_code: str = Field(description="订单编号order_code"),
                       reason: str = Field(description="取消原因reason，例如：不想取了"),
                       ) -> dict:
    biz = {
        'order_code': order_code,
        'reason': reason
    }
    url = f"{OPENAPI_URL_BASE}order/cancelOrder"
    return post_send(biz, url)


@mcp.tool(name="智能发单-跑男信息查询,查询跑腿实时信息", description="跑男信息查询，需要需要输入订单编号")
async def driver_track(order_code: str = Field(description="订单编号order_code"),  #
                       ) -> dict:
    biz = {
        'order_code': order_code,
    }
    url = f"{OPENAPI_URL_BASE}order/driverTrack"
    return post_send(biz, url)


def post_send(biz, url) -> dict:
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
        "X-App-Id": APP_ID,  # appid
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
    mcp.run()
# asyncio_run = asyncio.run(order_price("阳光城5号楼6层6号", "阳光城5号楼6层6号", "郑州市", ""))
# print(asyncio_run)
# asyncio.run(order_create("df3fc08498ff4ce3aa81219040f1f2f0", "18888888888"))
# asyncio.run(order_query("250418094610379000016927"))
