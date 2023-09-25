import datetime

from tinkoff.invest.async_services import InstrumentsService
from tinkoff.invest.utils import now
from datetime import datetime, timedelta

TOKEN = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'

import asyncio
import os
import re

from tinkoff.invest import (
	AsyncClient,  # асинхронный клиент
	OrderBookInstrument,  # для стаканов
	InstrumentStatus,
	CandleInstrument,
	MarketDataRequest,
	SubscribeCandlesRequest,
	SubscriptionAction,
	SubscriptionInterval,
	ShareType,
	CandleInterval,
	OrderDirection, OrderType, Quotation
)
from tinkoff.invest.utils import decimal_to_quotation, quotation_to_decimal
from decimal import Decimal

class Tinkoff_API:
	async def GetAccounts(self):
		async with AsyncClient(TOKEN) as client:
			return await client.users.get_accounts()

	# Поиск инструмента по тикеру
	async def FindInstruments(self, search_text):
		async with AsyncClient(TOKEN) as client:
			r = await client.instruments.find_instrument(query=search_text) # ищем по тикеру
			if(r.instruments): #если есть хоть какие то результаты
				for i in r.instruments: # перебираем результаты
					if(i.ticker == search_text): # проверяем на совпадение тикера
						if(re.search(r'^BBG', str(i.figi))): # проверяем чтобы FIGI начинался на BBG
							return i # возвращаем этот инструмент в виде ответа
			return False # если ничего не найдено или не соответствует условиям, то возвращаем False

	# Подробная информация о инструменте по UID
	async def InstrumentInfo(self, uid):
		async with AsyncClient(TOKEN) as client:
			info = await client.instruments.share_by(id_type=3,id=uid) # 1 для FIGI, 3 для UID
			return info.instrument

	async def InstrumentLastPrice(self, uid):
		async with AsyncClient(TOKEN) as client:
			last_price = await client.market_data.get_last_prices(instrument_id=[uid])
			last_price = float(quotation_to_decimal(last_price.last_prices[0].price))
			return last_price


	async def GetStreamInfo(self):
		async with AsyncClient(TOKEN) as client:
			self.market_data_stream: AsyncMarketDataStreamManager = (
				client.create_market_data_stream()
			)
			async for marketdata in self.market_data_stream:
				yield marketdata

	async def PositionsStream(self):
		async with AsyncClient(TOKEN) as client:
			accounts = ["XXXXXXXXXX"]
			async for portfolio in client.operations_stream.portfolio_stream(
				accounts=accounts
			):
				yield portfolio

	async def GetAllShares(self):
		async with AsyncClient(TOKEN) as client:
			instruments: InstrumentsService = client.instruments
			r = await instruments.shares(instrument_status=InstrumentStatus.INSTRUMENT_STATUS_ALL)
			for instr in r.instruments:
				if(instr.country_of_risk == "RU" and instr.currency == "rub" and instr.for_qual_investor_flag == False and instr.api_trade_available_flag == True and (instr.share_type == ShareType.SHARE_TYPE_PREFERRED or instr.share_type == ShareType.SHARE_TYPE_COMMON)):
					print(instr.uid+" - "+str(instr.short_enabled_flag)+" - "+str(instr.share_type)+" - "+instr.ticker+" - "+instr.name+" - "+str(instr.lot))
					

	async def AddStreamOrderBook(self, instrument, depth):
		self.market_data_stream.order_book.subscribe([
			OrderBookInstrument(instrument_id=instrument, depth=depth),
			#OrderBookInstrument(instrument_id="BBG000BT7ZK6", depth=50)
			])

	async def DelStreamOrderBook(self, instrument, depth):
		self.market_data_stream.order_book.unsubscribe([
			OrderBookInstrument(instrument_id=instrument, depth=depth)
			])

	async def Cancel_Orders(self):
		async with AsyncClient(TOKEN) as client:
			await client.cancel_all_orders(account_id="XXXXXXXXXX")

	async def Trade(self, instrument_id, quantity, type_order, direction, price):
		async with AsyncClient(TOKEN) as client:
			if(type_order == 'limit'):
				type_order = OrderType.ORDER_TYPE_LIMIT
			if(type_order == 'market'):
				type_order = OrderType.ORDER_TYPE_MARKET
			if(type_order == 'bestprice'):
				type_order = OrderType.ORDER_TYPE_BESTPRICE
			if(direction == 'buy'):
				direction = OrderDirection.ORDER_DIRECTION_BUY
			if(direction == 'sell'):
				direction = OrderDirection.ORDER_DIRECTION_SELL

			r = await client.orders.post_order(
				order_id=str(datetime.utcnow().timestamp()),
				instrument_id=instrument_id,
				quantity=quantity,
				account_id="XXXXXXXXXX",
				direction=direction,
				order_type=type_order,
				price=decimal_to_quotation(Decimal(price))
			)