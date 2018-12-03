import requests
from django.contrib import admin

# Register your models here.
from portfolio.models import Trade

@admin.register(Trade)
class TradeAdmin(admin.ModelAdmin):

    def time_seconds(self, obj):
        return obj.timestamp.strftime("%d/%m/%Y, %H:%M")

    # def total_investment(self, obj):
    #     return obj.price * obj.quantity
    #
    # def data(self, obj):
    #     data = requests.get('https://finance.yahoo.com/quote/%s/' % obj.ticker).text
    #     return data

    # def current_price(self, data):
    #     #currentPrice = str(data).split('"regularMarketPrice":{"raw":')[1].split(',"fmt":')[0]
    #     currentPrice = str(data)
    #     return currentPrice

    #print(type(data))
    #currentPrice = str(data).split('"regularMarketPrice":{"raw":')[1].split(',"fmt":')[0]

    #
    # def price_change(self, data):
    #     change = str(data).split('"regularMarketChangePercent":{"raw":')[1].split(',"fmt":"')[1].split('"},')[0]
    #     return change
    #
    # def pnl(self, obj):
    #     pnl = '%s%' % str((obj.current_price - obj.price) / obj.ice)
    #     return pnl

    time_seconds.admin_order_field = 'timestamp'
    time_seconds.short_description = 'Timestamp'

    # total_investment.short_description = 'Total Investment'
    #data.short_description = 'Data'
    #current_price.short_description = 'Current Price'
    # price_change.short_description = 'Delta'
    # pnl.short_description = 'Trade PnL'

    list_display = ('ticker',  'price', 'currency', 'quantity',  'time_seconds', 'long_name', 'instrument', 'total_investment', 'current_price', 'price_change', 'pnl')
    list_filter = ['timestamp']
