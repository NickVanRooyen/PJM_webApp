from datetime import datetime
import numpy as np

from django.core.exceptions import ValidationError
from django.forms import ModelForm, TextInput, Select
from bootstrap_datepicker_plus import DateTimePickerInput
import pdb

from portfolio.models import Trade


# create ModelForm class for Trade model, this will use all the same fields and field criteria
class TradeInputForm(ModelForm):
    class Meta:
        model = Trade
        fields = ['ticker', 'price', 'currency', 'quantity', 'timestamp', 'action']

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

    # custom validation of timestamp
    def clean_timestamp(self):
        data = self.cleaned_data['timestamp']
        if np.datetime64(data) > np.datetime64(datetime.today()):
            raise ValidationError('Time stamp is in the future')
        return data
