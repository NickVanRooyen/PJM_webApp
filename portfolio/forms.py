from datetime import datetime
import numpy as np
from django import forms

from django.core.exceptions import ValidationError
from django.forms import ModelForm, TextInput, Select
from bootstrap_datepicker_plus import DateTimePickerInput
import pdb

from portfolio.models import Trade, Accounts

# create ModelForm class for Trade model, this will use all the same fields and field criteria
class TradeInputForm(ModelForm):

    fee = forms.DecimalField(max_digits=20, decimal_places=2, label='Fee', required=False,
                             widget=TextInput(attrs={'class': 'form__input', 'placeholder': 'Fee'}))

    class Meta:
        model = Trade
        fields = ['ticker', 'price', 'currency', 'quantity', 'timestamp', 'action', 'fee',
                  'account']

        # set LANGUAGE_CODE = 'en-GB' in settings to get correct date format in picker
        # time format is HH for 24h, and have to use mm not MM for minutes
        widgets = {
            'ticker': TextInput(attrs={'class': 'form__input__top', 'placeholder': 'Ticker'}),
            'price': TextInput(attrs={'class': "form__input", 'placeholder': 'Price'}),
            'currency': Select(attrs={'class': 'form__input', 'placeholder': 'Currency', 'initial': 'Currency'}),
            'quantity': TextInput(attrs={'class': 'form__input', 'placeholder': 'Quantity'}),
            'timestamp': DateTimePickerInput(format='%d/%m/%Y HH:mm', attrs={'placeholder': 'Purchase Date'}),
            'action': Select(attrs={'class': 'form__input', 'placeholder': 'Action', 'initial': 'Action'}),
        }

    # add functionality to init to dynamically change the account field to a choice list of available broker accounts
    def __init__(self, *args, **kwargs):
        # call super init so that weperform original init, then perform our additional changes
        super(TradeInputForm, self).__init__(*args, **kwargs)
        choices = (('', 'Broker Account'),) + tuple(Accounts.objects.values_list('account', 'account'))
        # reset the field as a choice field
        self.fields['account'] = forms.ChoiceField(choices=choices, label="Broker Account", required=False,
                                                   help_text='Must have at least one broker account set up',
                                                   widget=Select(attrs={'class': 'form__input',
                                                                        'placeholder': 'Broker Account',
                                                                        'initial': 'Broker Account'}))

    # custom validation of timestamp
    def clean_timestamp(self):
        data = self.cleaned_data['timestamp']
        if np.datetime64(data) > np.datetime64(datetime.today()):
            raise ValidationError('Time stamp is in the future')
        return data

    def clean_ticker(self):
        data = self.cleaned_data['ticker']
        return data

    def clean_quantity(self):
        data = self.cleaned_data['quantity']
        if data <= 0:
            raise ValidationError('Quantity must be greater than 0')
        if self['action'].value() == 'sell':
            if self.cleaned_data['ticker'] in Trade.objects.values_list('ticker', flat=True):
                db_trade = Trade.objects.get(pk=self.cleaned_data['ticker'])
                if data > db_trade.quantity:
                    raise ValidationError('Specified "Quantity" larger than holdings: %s units' % db_trade.quantity)
            else:
                raise ValidationError('Specified "Ticker" not in Live Portfolio')
        return data

    def clean_fee(self):
        data = self.cleaned_data['fee']
        if data <= 0:
            raise ValidationError('Fee cannot be less than 0')
        return data

    def clean_account(self):
        accountInfo = Accounts.objects.get(pk=self.cleaned_data['account'])
        if accountInfo.ccy != self.cleaned_data['currency']:
            raise ValidationError('Input currency does not match account currency, input trade price and fees in '
                                  'currency of Broker account')
        if self.cleaned_data['action'] == 'buy':
            totalSpend = self.cleaned_data['quantity'] * self.cleaned_data['price'] + self.cleaned_data['fee']
            if totalSpend > accountInfo.balance:
                raise ValidationError('Cost of trade greater than Broker Account balance, add cash to facilitate trade')
        return self.cleaned_data['account']

# create ModelForm class for CashAccount model, this will use all the same fields and field criteria
class AccountInputForm(ModelForm):

    class Meta:
        model = Accounts
        fields = ['broker', 'ccy', 'balance']

        widgets = {
            'broker': TextInput(attrs={'class': 'form__input__top', 'placeholder': 'Broker'}),
            'ccy': Select(attrs={'class': 'form__input', 'placeholder': 'Currency', 'initial': 'Currency'}),
            'balance': TextInput(attrs={'class': 'form__input', 'placeholder': 'Balance'}),
        }

    # custom validation of account balance
    def clean_balance(self):
        data = self.cleaned_data['balance']
        if data < 0:
            raise ValidationError('Balance must be greater than 0')
        return data


# create ModelForm class for editing portfolio line items, this will use all the same fields and field criteria
class PortfolioEditForm(ModelForm):

    class Meta:
        model = Trade
        fields = ['ticker', 'price', 'currency', 'quantity', 'timestamp', 'action', 'account', 'sector', 'industry',
                  'long_name', 'instrument']

        widgets = {
            'ticker': TextInput(attrs={'class': 'form__input__top', 'placeholder': 'Ticker'}),
            'long_name': TextInput(attrs={'class': "form__input", 'placeholder': 'Long Name'}),
            'instrument': TextInput(attrs={'class': "form__input", 'placeholder': 'Instrument'}),
            'sector': TextInput(attrs={'class': "form__input", 'placeholder': 'Sector'}),
            'industry': TextInput(attrs={'class': "form__input", 'placeholder': 'Industry'}),
            'price': TextInput(attrs={'class': "form__input", 'placeholder': 'Price'}),
            'currency': Select(attrs={'class': 'form__input', 'placeholder': 'Currency', 'initial': 'Currency'}),
            'quantity': TextInput(attrs={'class': 'form__input', 'placeholder': 'Quantity'}),
            'timestamp': DateTimePickerInput(format='%d/%m/%Y HH:mm', attrs={'placeholder': 'Purchase Date'}),
            'action': Select(attrs={'class': 'form__input', 'placeholder': 'Action', 'initial': 'Action'}),
        }

    # add functionality to init to dynamically change the account field to a choice list of available broker accounts
    def __init__(self,ticker, long_name, instrument,sector, industry, price, currency, quantity, timestamp, action,
                 account,
                 *args, **kwargs):
        # call super init so that weperform original init, then perform our additional changes
        super(PortfolioEditForm, self).__init__(*args, **kwargs)
        choices = (('', 'Broker Account'),) + tuple(Accounts.objects.values_list('account', 'account'))
        # reset the field as a choice field
        self.fields['account'] = forms.ChoiceField(choices=choices, label="Broker Account", required=False,
                                                   help_text='Must have at least one broker account set up',
                                                   widget=Select(attrs={'class': 'form__input',
                                                                        'placeholder': 'Broker Account'}))
        self.fields['ticker'].initial = ticker
        self.fields['long_name'].initial = long_name
        self.fields['instrument'].initial = instrument
        self.fields['sector'].initial = sector
        self.fields['industry'].initial = industry
        self.fields['price'].initial = price
        self.fields['currency'].initial = currency
        self.fields['quantity'].initial = quantity
        self.fields['timestamp'].initial = timestamp
        self.fields['action'].initial = action


