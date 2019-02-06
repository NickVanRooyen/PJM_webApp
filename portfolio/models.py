import requests
from django.db import models

# Create your models here.

# portfolio model to store portfolio info
from django.urls import reverse
import pdb


class TradeHistory(models.Model):
    """ model for trade history """
    # set ticker as primary key
    ticker = models.CharField(max_length=7)
    price = models.DecimalField(max_digits=20, default=0.0, decimal_places=2)
    currency = models.CharField(max_length=3, help_text='3 letter currency code')
    quantity = models.IntegerField(default=0)
    # ensure input format when compiling form
    timestamp = models.DateTimeField(help_text='Enter purchase details"')
    id = models.CharField(max_length=100, primary_key=True)
    action = models.CharField('Action', max_length=4)
    account = models.CharField('Broker Account', max_length=20, blank=True)
    fee = models.DecimalField(max_digits=20, default=0.0, decimal_places=2)
    sector = models.CharField('Sector', max_length=50, blank=True)
    industry = models.CharField('Industry', max_length=50, blank=True)
    long_name = models.CharField('Long Name', max_length=50, blank=True)
    instrument = models.CharField('Instrument', max_length=50, blank=True)

    def save(self, *args, **kwargs):
        self.id = '%s_%s' % (self.ticker, str(self.timestamp))
        super(TradeHistory, self).save(*args, **kwargs)


class Trade(models.Model):
    """ model for trade instances """

    ACTIONS = (('', 'Action'),
               ("buy", "BUY"),
               ("sell", "SELL"),)

    CCYS = (('', 'Currency'),
            ("EUR", "EUR"),
            ("GBP", "GBP"),
            ("USD", "USD"),)

    # set ticker as primary key
    ticker = models.CharField('Ticker', max_length=7, primary_key=True, blank=True)
    price = models.DecimalField('Price', max_digits=20, decimal_places=2, blank=True)
    currency = models.CharField('Currency', max_length=3,  choices=CCYS, help_text='3 letter currency code', blank=True)
    quantity = models.IntegerField('Quantity', blank=True)
    # ensure input format when compiling form
    timestamp = models.DateTimeField('TimeStamp', help_text='Enter purchase date and time"', blank=True)
    action = models.CharField('Action', max_length=4, choices=ACTIONS, help_text='"BUY" or "SELL"', blank=True)
    account = models.CharField('Broker Account', max_length=20, blank=True)
    sector = models.CharField('Sector', max_length=50, blank=True)
    industry = models.CharField('Industry', max_length=50, blank=True)
    long_name = models.CharField('Long Name', max_length=50, blank=True)
    instrument = models.CharField('Instrument', max_length=50, blank=True)

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


# method to set primary key
def get_account(broker, ccy):
    return '%s_%s' % (broker, ccy)


class Accounts(models.Model):
    """ model for cash accounts """

    CCYS = (('', 'Currency'),
            ("EUR", "EUR"),
            ("GBP", "GBP"),
            ("USD", "USD"),)

    # set ticker as primary key
    # define account that holds cash
    account = models.CharField('Account Name', max_length=20, blank=True, primary_key=True)
    broker = models.CharField('Broker', max_length=20, blank=True)
    ccy = models.CharField('Currency Account', max_length=3, blank=True, choices=CCYS)
    balance = models.DecimalField('Balance', max_digits=20, decimal_places=2, blank=True)

    # override the save method to create an account id before saving.
    def save(self, *args, **kwargs):
        self.account = '%s_%s' % (self.broker, self.ccy)
        super(Accounts, self).save(*args, **kwargs)

    def __str__(self):
        # string to be used to represent the account instance
        return self.account


