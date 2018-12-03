import requests
from django.db import models

# Create your models here.

# portfolio model to store portfolio info
from django.urls import reverse


class TradeHistory(models.Model):
    """ model for trade history """
    # set ticker as primary key
    ticker = models.CharField(max_length=7, null=False, blank=False)
    price = models.DecimalField(null=False, blank=False, max_digits=20, default=0.0, decimal_places=2)
    currency = models.CharField(null=False, blank=False, max_length=3, help_text='3 letter currency code')
    quantity = models.IntegerField(null=False, blank=False, default=0)
    # ensure input format when compiling form
    timestamp = models.DateTimeField(null=False, blank=False, help_text='Enter purchase details"')
    id = models.CharField(max_length=100, null=False, blank=False, primary_key=True)
    action = models.CharField('Action', max_length=4, null=False, blank=False, help_text='"Buy" or "Sell"')

    def save(self):
        self.id = '%s_%s' % (self.ticker, str(self.timestamp))
        super(TradeHistory, self).save()


class Trade(models.Model):
    """ model for trade instances """
    # set ticker as primary key
    ticker = models.CharField('Ticker', max_length=7, null=False, blank=False, primary_key=True)
    price = models.DecimalField('Price', null=False, blank=False, max_digits=20, default=0.0, decimal_places=2)
    currency = models.CharField('Currency', null=False, blank=False, max_length=3, help_text='3 letter currency code')
    quantity = models.IntegerField('Quantity', null=False, blank=False, default=0)
    # ensure input format when compiling form
    timestamp = models.DateTimeField('TimeStamp', null=False, blank=False, help_text='Enter purchase date and time"')
    action = models.CharField('Action', max_length=4, null=False, blank=False, help_text='"Buy" or "Sell"')

    long_name = 'N/A'
    instrument = 'N/A'
    current_price = 'N/A'
    price_change = 'N/A'
    pnlPercent = 'N/A'
    pnl = 'N/A'

    @property
    def total_investment(self):
        return float(self.price) * float(self.quantity)

    def __str__(self):
        # string to be used to represent the trade instance
        return self.ticker
    #
    # def get_absolute_url(self):
    #     # return the url to access the detail record of this trade
    #     return reverse('trade-detail', args=[str(self.ticker)])
