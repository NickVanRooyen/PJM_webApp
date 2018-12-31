from datetime import datetime

from django.core.exceptions import ValidationError
from django.forms import ModelForm, TextInput, Select
from bootstrap_datepicker_plus import DateTimePickerInput

from portfolio.models import Trade


# create ModelForm class for Trade model, this will use all the same fields and field criteria
class TradeInputForm(ModelForm):
    class Meta:
        model = Trade
        fields = '__all__'

        widgets = {
            'ticker': TextInput(attrs={'class': 'form__input__top', 'placeholder': 'Ticker'}),
            'price': TextInput(attrs={'class': "form__input", 'placeholder': 'Price'}),
            'currency': TextInput(attrs={'class': 'form__input', 'placeholder': 'Currency'}),
            'quantity': TextInput(attrs={'class': 'form__input', 'placeholder': 'Quantity'}),
            'timestamp': DateTimePickerInput(format='%d/%m/%Y HH:MM', attrs={'placeholder': 'Purchase Date'}),
            'action': Select(attrs={'class': 'form__input', 'placeholder': 'Action', 'initial': 'Action'}),
        }

    # custom validation of timestamp
    def clean_timestamp(self):
        data = self.cleaned_data['timestamp']
        if data > datetime.date.today():
            raise ValidationError('Time stamp is in the future')
