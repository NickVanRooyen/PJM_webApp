from datetime import datetime
import numpy as np
from django import forms
import portfolio.config as config

from django.core.exceptions import ValidationError
from django.forms import ModelForm, TextInput, Select
from bootstrap_datepicker_plus import DateTimePickerInput
import pdb

from portfolio.models import Trade, Accounts, TradeHistory


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

    # set a default fee for the input form
    fee = forms.DecimalField(widget=TextInput(attrs={'class': 'form__input__round',
                                                     'placeholder': 'Fee', 'initial': 'Fee'}))

    class Meta:
        model = Trade
        fields = ['ticker', 'price', 'currency', 'quantity', 'timestamp', 'action', 'account', 'sector', 'industry',
                  'long_name', 'instrument', 'fee']

        widgets = {
            'ticker': TextInput(attrs={'class': 'form__input__round', 'placeholder': 'Ticker'}),
            'long_name': TextInput(attrs={'class': "form__input__round", 'placeholder': 'Long Name'}),
            'instrument': TextInput(attrs={'class': "form__input__round", 'placeholder': 'Instrument'}),
            'sector': TextInput(attrs={'class': "form__input__round", 'placeholder': 'Sector'}),
            'industry': TextInput(attrs={'class': "form__input__round", 'placeholder': 'Industry'}),
            'price': TextInput(attrs={'class': "form__input__round", 'placeholder': 'Price'}),
            'currency': Select(attrs={'class': 'form__input__round', 'placeholder': 'Currency', 'initial': 'Currency'}),
            'quantity': TextInput(attrs={'class': 'form__input__round', 'placeholder': 'Quantity'}),
            'timestamp': DateTimePickerInput(format='%d/%m/%Y HH:mm', attrs={'placeholder': 'Purchase Date'}),
            'action': Select(attrs={'class': 'form__input__round', 'placeholder': 'Action', 'initial': 'Action'})
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
                                                   widget=Select(attrs={'class': 'form__input__round',
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
        self.fields['account'].initial = account
        self.fields['fee'].initial = 0.0


# create ModelForm class for editing trade history line items, this will use all the same fields and field criteria
class HistoryEditForm(ModelForm):

    class Meta:
        model = TradeHistory
        fields = ['ticker', 'price', 'currency', 'quantity', 'timestamp', 'action', 'account', 'sector', 'industry',
                  'long_name', 'instrument', 'fee', 'id']

        widgets = {
            'ticker': TextInput(attrs={'class': 'form__input__round', 'placeholder': 'Ticker'}),
            'id': TextInput(attrs={'class': 'form__input__round', 'placeholder': 'ID'}),
            'fee': TextInput(attrs={'class': 'form__input__round', 'placeholder': 'Fee'}),
            'long_name': TextInput(attrs={'class': "form__input__round", 'placeholder': 'Long Name'}),
            'instrument': TextInput(attrs={'class': "form__input__round", 'placeholder': 'Instrument'}),
            'sector': TextInput(attrs={'class': "form__input__round", 'placeholder': 'Sector'}),
            'industry': TextInput(attrs={'class': "form__input__round", 'placeholder': 'Industry'}),
            'price': TextInput(attrs={'class': "form__input__round", 'placeholder': 'Price'}),
            'quantity': TextInput(attrs={'class': 'form__input__round', 'placeholder': 'Quantity'}),
            'timestamp': DateTimePickerInput(format='%d/%m/%Y HH:mm', attrs={'placeholder': 'Purchase Date'}),
        }

    # add functionality to init to dynamically change the account field to a choice list of available broker accounts
    def __init__(self,ticker, long_name, instrument,sector, industry, price, currency, quantity, timestamp, action,
                 account, id, fee,
                 *args, **kwargs):
        # call super init so that weperform original init, then perform our additional changes
        super(HistoryEditForm, self).__init__(*args, **kwargs)
        choices = (('', 'Broker Account'),) + tuple(Accounts.objects.values_list('account', 'account'))
        # reset the field as a choice field
        self.fields['account'] = forms.ChoiceField(choices=choices, label="Broker Account", required=False,
                                                   help_text='Must have at least one broker account set up',
                                                   widget=Select(attrs={'class': 'form__input__round',
                                                                        'placeholder': 'Broker Account'}))
        self.fields['currency'] = forms.ChoiceField(choices=config.CCYS, label="Currency", required=False,
                                                    help_text='Must select a currency',
                                                    widget=Select(attrs={'class': 'form__input__round',
                                                                         'placeholder': 'Currency'}))
        self.fields['action'] = forms.ChoiceField(choices=config.ACTIONS, label="Action", required=False,
                                                  help_text='Must select an Action',
                                                  widget=Select(attrs={'class': 'form__input__round',
                                                                       'placeholder': 'Action'}))

        self.fields['ticker'].initial = ticker
        self.fields['long_name'].initial = long_name
        self.fields['instrument'].initial = instrument
        self.fields['sector'].initial = sector
        self.fields['industry'].initial = industry
        self.fields['price'].initial = price
        self.fields['currency'].initial = currency
        self.fields['quantity'].initial = quantity
        self.fields['timestamp'].initial = timestamp
        self.fields['account'].initial = account
        self.fields['id'].initial = id
        self.fields['fee'].initial = fee
        self.fields['action'].initial = action


# create ModelForm class for editing trade history line items, this will use all the same fields and field criteria
class AccountEditForm(ModelForm):

    class Meta:
        model = Accounts
        fields = ['account', 'broker', 'ccy', 'balance']

        widgets = {
            'account': TextInput(attrs={'class': 'form__input__round', 'placeholder': 'Ticker'}),
            'broker': TextInput(attrs={'class': 'form__input__round', 'placeholder': 'ID'}),
            'ccy': TextInput(attrs={'class': 'form__input__round', 'placeholder': 'Fee'}),
            'balance': TextInput(attrs={'class': "form__input__round", 'placeholder': 'Balance'})
        }

    def __init__(self, account, broker, ccy, balance,
                 *args, **kwargs):
        # call super init so that we perform original init, then perform our additional changes
        super(AccountEditForm, self).__init__(*args, **kwargs)

        self.fields['account'].initial = account
        self.fields['broker'].initial = broker
        self.fields['ccy'].initial = ccy
        self.fields['balance'].initial = balance



