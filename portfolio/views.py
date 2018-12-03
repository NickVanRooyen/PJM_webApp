import requests
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views import generic

from portfolio.forms import TradeInputForm
from portfolio.models import Trade


class TradeListView(generic.ListView):
    model = Trade

    # override the "get_queryset" function so that can update the fields from the model for display purposes without
    # changing the underlying models fields
    def get_queryset(self):
        queryset = super(TradeListView, self).get_queryset()
        for obj in queryset:
            # try to get most up to date market info and update calculations. If web page not available want to display
            # "N/A", otherwise raise the error.
            try:
                data = requests.get('https://finance.yahoo.com/quote/%s/' % obj.ticker).text
                current_price = float(data.split('"regularMarketPrice":{"raw":')[1].split(',"fmt":')[0])
                obj.current_price = '{:,.2f}'.format(current_price)
                obj.price_change = data.split('"regularMarketChangePercent":{"raw":')[1].split(',"fmt":"')[1].split('"},')[0]
                obj.long_name = data.split(',"longName":"')[1].split('"')[0]
                obj.instrument = data.split(',"quoteType":"')[1].split('"')[0]
                obj.pnlPercent = '{:,.2f}%'.format(((float(current_price) - float(obj.price)) /
                                                     float(obj.price))*100)
                obj.pnl = '{:,.2f}'.format(((float(current_price) - float(obj.price)) /
                                               float(obj.price))*float(obj.total_investment))
            except requests.exceptions.ConnectionError:
                pass
            except Exception as e:
                raise e

            obj.total_investment_format = '{:,.2f}'.format(float(obj.total_investment))
            obj.price = '{:,.2f}'.format(float(obj.price))
            obj.timestamp = str(obj.timestamp.strftime('%d-%m-%Y   %H:%M'))
        return queryset


def tradeInputView(request):
    """View function for entering trade info."""

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = TradeInputForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('portfolio'))

    # If this is a GET (or any other method) create the default form.
    else:
        form = TradeInputForm

    context = {
        'form': form
    }

    return render(request, 'portfolio/trade_input.html', context)
