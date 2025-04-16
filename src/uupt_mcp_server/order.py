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

APP_ID=os.getenv("APP_ID")
APP_SECRET=os.getenv("APP_SECRET")
OPEN_ID=os.getenv("OPEN_ID")
OPENAPI_URL_BASE=os.getenv("OPENAPI_URL_BASE")


# 创建MCP服务器实例
mcp = FastMCP("mcp-server-uupt-orders")


@mcp.tool()
async def order_price(from_address: str,  # 开始地址，例如：阳光城5号楼6层6号
    to_address: str,    # 结束地址，例如：楷林国际4层210号
    sender_phone: str,  # 发件人电话，例如：18688888888
    receiver_phone: str, # 收件人电话，例如：15288888888
     ctx: Context,
    city_name: str = '郑州市',  # 城市名称，默认郑州
    send_type: str = '0'    # 配送类型，默认0,
    )-> dict:
    
    """
    Name:
        智能发单-订单询价
        
    Description:
        查询订单价格，需要需要输入开始地址，结束地址。
        
    Args:
        from_address: 开始地址，要求完整地址信息
        to_address: 结束地址，要求完整地址信息
        city_name: 城市名称，默认郑州市
        send_type: 配送类型，默认0
        
    """
    payload = {
        'appid': APP_ID,
        'openid': OPEN_ID,
        'nonce_str': str(uuid.uuid1()).replace('-', '').lower(),
        'timestamp': int(time.time()),
        'from_address': from_address,
        'to_address': to_address,
        'city_name': city_name,
        'send_type': send_type,
    }

    sortedPayload = {key: payload[key] for key in sorted(payload.keys())}
    arr = [f'{key}={sortedPayload[key]}' for key in sortedPayload]
    arr.append(f'key={APP_SECRET}')
    signature_string = '&'.join(arr).upper()
    sign = hashlib.md5(signature_string.encode(encoding='UTF-8')).hexdigest().upper()
    sortedPayload['sign'] = sign

    print(f"请求参数: {json.dumps(sortedPayload, ensure_ascii=False, indent=4)}")

    try:
        print(f"请求URL: {OPENAPI_URL_BASE}getorderprice.ashx")
        res = requests.post(f'{OPENAPI_URL_BASE}getorderprice.ashx', data=sortedPayload)
        if res.status_code == 200:
            return res.json()
        else:
            print(f"Error: {res.status_code}, {res.text}")
            return '错误'
    except requests.RequestException as e:
        print(f"An error occurred: {e}")


@mcp.tool()
async def order_create(price_token: str,  # 计算订单价格接口返回的price_token
    total_money: str,    # 订单总额，计算订单价格接口返回的total_money
    need_paymoney: str,  # 订单需要支付的金额，实际需要支付金额，计算订单价格接口返回的need_paymoney
    receiver_phone: str, # 收件人电话，例如：15288888888
     ctx: Context,
    )-> dict:
    
    """
    Name:
        智能发单-创建订单
        
    Description:
        自动创建订单，需要需要输入：
        计算订单价格接口返回的price_token，
        计算订单价格接口返回的total_money，实际需要支付金额，
        计算订单价格接口返回的need_paymoney，
        收件人电话。
        
    Args:
        price_token: 计算订单价格接口返回的price_token
        total_money: 计算订单价格接口返回的total_money，实际需要支付金额，
        need_paymoney: 计算订单价格接口返回的need_paymoney
        receiver_phone: 收件人联系电话
    """

    payload = {
        'appid': APP_ID,
        'openid': OPEN_ID,
        'nonce_str': str(uuid.uuid1()).replace('-', '').lower(),
        'timestamp': int(time.time()),
        'price_token': price_token,
        'order_price': total_money,
        'balance_paymoney': need_paymoney,
        'receiver_phone': receiver_phone
    }

    sortedPayload = {key: payload[key] for key in sorted(payload.keys())}
    arr = [f'{key}={sortedPayload[key]}' for key in sortedPayload]
    arr.append(f'key={APP_SECRET}')
    signature_string = '&'.join(arr).upper()
    sign = hashlib.md5(signature_string.encode(encoding='UTF-8')).hexdigest().upper()
    sortedPayload['sign'] = sign
 
 
    try:
        res = requests.post(f'{OPENAPI_URL_BASE}addorder.ashx', data=sortedPayload)
        if res.status_code == 200:
            return res.json()
        else:
            print(f"Error: {res.status_code}, {res.text}")
            return '错误'
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
 
@mcp.tool()
async def order_query(order_code: str,  # 订单编号order_code
     ctx: Context,
    )-> dict:
    
    """
    Name:
        智能发单-获取订单详情
        
    Description:
        获取订单详情，需要需要输入订单编号：
        订单编号order_code

        
    Args:
        order_code: 订单编号order_code
    """

    payload = {
        'appid': APP_ID,
        'openid': OPEN_ID,
        'nonce_str': str(uuid.uuid1()).replace('-', '').lower(),
        'timestamp': int(time.time()),
        'order_code': order_code
    }

    sortedPayload = {key: payload[key] for key in sorted(payload.keys())}
    arr = [f'{key}={sortedPayload[key]}' for key in sortedPayload]
    arr.append(f'key={APP_SECRET}')
    signature_string = '&'.join(arr).upper()
    sign = hashlib.md5(signature_string.encode(encoding='UTF-8')).hexdigest().upper()
    sortedPayload['sign'] = sign
 
    try:
        res = requests.post(f'{OPENAPI_URL_BASE}getorderdetail.ashx', data=sortedPayload)
        if res.status_code == 200:
            return res.json()
        else:
            print(f"Error: {res.status_code}, {res.text}")
            return '错误'
    except requests.RequestException as e:
        print(f"An error occurred: {e}")


@mcp.tool()
async def order_cancel(order_code: str,  # 订单编号order_code
     reason: str, # 取消原因reason，例如：不想取了
     ctx: Context,
    )-> dict:

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

    payload = {
        'appid': APP_ID,
        'openid': OPEN_ID,
        'nonce_str': str(uuid.uuid1()).replace('-', '').lower(),
        'timestamp': int(time.time()),
        'order_code': order_code,
        'reason': reason
    }

    sortedPayload = {key: payload[key] for key in sorted(payload.keys())}
    arr = [f'{key}={sortedPayload[key]}' for key in sortedPayload]
    arr.append(f'key={APP_SECRET}')
    signature_string = '&'.join(arr).upper()
    sign = hashlib.md5(signature_string.encode(encoding='UTF-8')).hexdigest().upper()
    sortedPayload['sign'] = sign
 
    try:
        res = requests.post(f'{OPENAPI_URL_BASE}cancelorder.ashx', data=sortedPayload)
        if res.status_code == 200:
            return res.json()
        else:
            print(f"Error: {res.status_code}, {res.text}")
            return '错误'
    except requests.RequestException as e:
        print(f"An error occurred: {e}")




if __name__ == "__main__":
    mcp.run()