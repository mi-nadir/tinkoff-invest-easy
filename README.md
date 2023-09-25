# Класс для работы с Тинькофф Инвест API на Python

Проверен на Pythom 3.8, в файле class_tinkoff_api.py редактируем строки с "иксами"
```
TOKEN = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
accounts = ["XXXXXXXXXX"]
.....
```
Создаем рядом свой файл, например main.py, импортируем модули и классы
```
from class_tinkoff_api import Tinkoff_API
import asyncio
.....
```
Создаем экземпляр класса
```
tinkoff = Tinkoff_API()
```
### Пример кода для асинхронной работы с Tinkoff Invest API
Функция для создания новой заявки
* второй агрумент в tinkoff.Trade - это кол-во лотов
* третий аргумент - тип заявки (принимает limit, market, bestprice)
* четвертый - покупка или продажа (принимает sell, buy)
* В конце пример подписки на стакан
```
async def NewTrade(instrument_info, long_or_short):
	last_price = await tinkoff.InstrumentLastPrice(instrument_info.uid) #узнаем последнюю цену

	if(long_or_short == 'long'):
		await tinkoff.Trade(instrument_info.figi, 1, 'limit', 'buy', str(last_price))
	if(long_or_short == 'short'):
		await tinkoff.Trade(instrument_info.figi, 1, 'limit', 'sell', str(last_price))

	await SubscribeToOrderBook(instrument_info)
```
Функция для подписки / отписки от стакана

Как второй аргумент в tinkoff.AddStreamOrderBook можно передать 1, 10, 20, 30, 40, 50 - это размер стакана
```
async def SubscribeToOrderBook(instrument_info):
	await tinkoff.AddStreamOrderBook(instrument_info.uid, 10)

	await asyncio.sleep(1200)

	await tinkoff.DelStreamOrderBook(instrument_info.uid, 10)
```
Функция для чтения информации после подписки на стакан (чтение стрима)

В стрим передает так же и другую информацию которую можно читать (в основном после подписки)
```
async def StreamParser():
	async for info in tinkoff.GetStreamInfo():
		# если со стрима пришла информация о стакане
		if(info.orderbook != None):
			print("FIGI: "+str(info.orderbook.figi))
			print("Кол-во позиций в стакане: "+str(info.orderbook.depth))
			print("Все заявки попали в стакан (если False то сетевые задержки или нарушение порядка доставки): "+str(info.orderbook.is_consistent))
			print("Instrument UID: "+str(info.orderbook.instrument_uid))
			print("Время: "+str(info.orderbook.time))
			buff_limit_up = info.orderbook.limit_up.units+(info.orderbook.limit_up.nano*0.000000001)
			print("Верхний лимит цены за 1 инструмент (не лота): "+str(buff_limit_up))
			buff_limit_down = info.orderbook.limit_down.units+(info.orderbook.limit_down.nano*0.000000001)
			print("Нижний лимит цены за 1 инструмент (не лота): "+str(buff_limit_down))
		if(info.ping != None):
			print('Проверка активности стрима:')
			print(info.ping)
		if(info.candle != None):
			print('Свеча:')
			print(info.candle)
		if(info.trade != None):
			print('Сделки:')
			print(info.trade)
		if(info.trading_status != None):
			print('Торговый статус:')
			print(info.trading_status)
```
Пример вывода информации о счетах которые доступны для управления в текущем токене, ниже отмена всех выставленных заявок на текущий момент
```
async def OnStartProgram():
	info = await tinkoff.GetAccounts()
	for accs in info.accounts:
		text = "ID: "+str(accs.id)+" - "+accs.name
		if(accs.type == 1):
			text += " - Брокерский счет"
		if(accs.type == 2):
			text += " - ИИС"
		if(accs.type == 3):
			text += " - Инвесткопилка"
		if(accs.access_level == 1):
			text += " - Полный доступ"
		if(accs.access_level == 2):
			text += " - Только чтение"
		if(accs.access_level == 3):
			text += " - Нет доступа"
		if(accs.status == 1):
			text += " - В процессе открытия"
		if(accs.status == 3):
			text += " - Закрытый счет"
		print(text)

	await tinkoff.Cancel_Orders()
```
Запуск основных функций
* Вывод информации о счетах
* Запуск парсера (подписка должна осуществяться отдельно)
* Вывод информации об инструментах
```
async def main():
	on_start = asyncio.create_task(OnStartProgram())
	stream_parser = asyncio.create_task(StreamParser())
	starter = asyncio.create_task(tinkoff.GetAllShares())
	await asyncio.gather(on_start, stream_parser, starter)
```
Запуск асинхронной программы
```
asyncio.run(main())
```
