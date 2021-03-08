import sys
from portfolio import config
sys.path.append(config.code_path)

from decimal import Decimal

import django
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "PJM_webApp.settings")
django.setup()

import pandas as pd

import requests
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views import generic
import pdb
from django.contrib.auth.models import User

from django.views.generic import TemplateView

from dataUtils.dataUtils import dBaseAction, writeDBv2
import AlgorithcTrading.config.stocks as stocks
from portfolio.database_data import get_map_chart, get_volatility_chart, get_market_chart, get_backtest_chart, \
    get_crypto_charts, update_db_portfolio, get_market_backtest_chart, get_market_reversion_chart
from portfolio.forms import TradeInputForm, AccountInputForm, PortfolioEditForm, HistoryEditForm, AccountEditForm, \
    LoginForm, CreateUserForm
from portfolio.models import Trade, Accounts, TradeHistory


def loginView(request):

    # If this is a POST request then process the Form data
    if request.method == 'POST':
        # Create a form instance and populate it with data from the request (binding):
        form = LoginForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return HttpResponseRedirect(reverse('portfolio'))
            else:

                # add custom error to form
                form.add_error('username', 'Username and Password combination not found...')
                print(form.errors)

            # create a user based on the inputs
            #user = User.objects.create_user(username=, email=, password=)
            #user.save()

        else:
            print(form.errors)

    # If this is a GET (or any other method) create the default form.
    else:
        form = LoginForm

    context = {
        'form': form
    }

    return render(request, 'portfolio/login.html', context)


def createUserView(request):

    # If this is a POST request then process the Form data
    if request.method == 'POST':
        # Create a form instance and populate it with data from the request (binding):
        form = CreateUserForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            username = request.POST['username']
            email = request.POST['email']
            password = request.POST['password']

            user = User.objects.create_user(username=username, email=email, password=password)
            pdb.set_trace()
            user.save()

            # create a new portfolio, order history and account for user by using 1st row from master table
            portfolio_columns = dBaseAction(stocks.dBase,""" select * from %s limit 1""" % stocks.web_portfolio)[0].columns
            orderHistory_columns = dBaseAction(stocks.dBase,""" select * from %s limit 1""" % stocks.web_order_history)[0].columns
            accounts_columns = dBaseAction(stocks.dBase,""" select * from %s limit 1""" % stocks.web_accounts)[0].columns

            writeDBv2(stocks.dBase, '%s_%s' % (stocks.web_portfolio, username), pd.DataFrame([], columns=portfolio_columns))



            return HttpResponseRedirect(reverse('portfolio'))

        else:
            print(form.errors)

    # If this is a GET (or any other method) create the default form.
    else:
        form = CreateUserForm

    context = {
        'form': form
    }

    return render(request, 'portfolio/create_login.html', context)

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

        # first get the model pk we are looking for
        postpk = request.POST.get('ticker', None)

        # get the model from the db
        model, created = Trade.objects.get_or_create(pk=postpk)

        # Create a form instance and populate it with data from the request, either populates existing model instance
        # or creates a new instance ( thus allows access already stored primary key:
        form = TradeInputForm(request.POST, instance=model)

        # Check if the form is valid:
        if form.is_valid():

            instance = form.save(commit=False)

            data = requests.get('https://finance.yahoo.com/quote/%s/' % instance.ticker).text
            instance.long_name = data.split(',"longName":"')[1].split('"')[0]
            instance.instrument = data.split(',"quoteType":"')[1].split('"')[0]
            instance.sector = data.split('"sector":"')[1].split('"')[0]
            instance.industry = data.split('"industry":"')[1].split('"')[0]

            # adjust account holdings based on actions and fees
            account = Accounts.objects.get(pk=instance.account)
            totalSpend = float(instance.quantity) * float(instance.price)
            if instance.action == 'sell':
                account.balance += Decimal(totalSpend)
            else:
                account.balance -= Decimal(totalSpend)
            # fee is always negative
            account.balance -= Decimal(form.cleaned_data['fee'])
            account.save()

            # update trade history
            tradeHistory = TradeHistory()
            for x, y in form.cleaned_data.items():
                setattr(tradeHistory, x, y)
            setattr(tradeHistory, 'long_name', instance.long_name)
            setattr(tradeHistory, 'instrument', instance.instrument)
            setattr(tradeHistory, 'sector', instance.sector)
            setattr(tradeHistory, 'industry', instance.industry)
            tradeHistory.save()

            # test if trade ticker already exists and adjust holdings average price to reflect new amount.
            # if new amount is 0, then delete entry
            tickers = Trade.objects.values_list('ticker', flat=True)
            # when doing instance.save(commit=False) it will populate the database with the primary key and now other
            # data, so if key is populated must ensure that price is also populated before doing price adjustments,
            # otherwise must simply add new trade
            present_populated = False
            if instance.ticker in tickers:
                db_trade = Trade.objects.get(pk=instance.ticker)
                if db_trade.price is not None: present_populated = True

            if present_populated:
                adjust_quantity = instance.quantity

                if instance.action == 'sell':
                    adjust_quantity *= -1

                # Average price only adjusts when you buy.
                # When you sell the average purchase price remains constant, just with a smaller number of contracts
                if instance.action == 'buy':
                    db_trade.price = (instance.price * adjust_quantity +
                                      db_trade.price * db_trade.quantity) / \
                                     (adjust_quantity + db_trade.quantity)
                db_trade.quantity = db_trade.quantity + adjust_quantity

                if db_trade.quantity == 0:
                    db_trade.delete()
                else:
                    db_trade.save()

            else:
                # saves to database
                instance.save()

            # update mongo database to reflect data in webpage database
            update_db_portfolio()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('portfolio'))
        else:
            ## use pcb to debug django in console
            #pdb.set_trace()
            print(form.errors)

    # If this is a GET (or any other method) create the default form.
    else:
        form = TradeInputForm

    context = {
        'form': form
    }

    return render(request, 'portfolio/trade_input.html', context)


class TradeHistoryListView(generic.ListView):
    model = TradeHistory


class AccountListView(generic.ListView):
    model = Accounts


def accountInputView(request):
    """View function for entering account info."""

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = AccountInputForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            form.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('accounts'))
        else:
            ## use pcb to debug django in console
            # pdb.set_trace()
            print(form.errors)

    # If this is a GET (or any other method) create the default form.
    else:
        form = AccountInputForm

    context = {
        'form': form
    }

    return render(request, 'portfolio/accounts_input.html', context)


def portfolioEditView(request):
    """View function for entering account info."""

    # unpack the get request to retrieve ticker that we are editing
    ticker = [*request.GET.keys()][0]
    # get the model from the db
    model, created = Trade.objects.get_or_create(pk=ticker)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        #pdb.set_trace()
        # add fee to model
        #setattr(model, 'fee', request.POST['fee'])
        # Create a form instance and populate it with data from the request (binding):
        form = TradeInputForm(request.POST, instance=model)

        # Check if the form is valid:
        if form.is_valid():
            form.save()
            # update mongo database to reflect data in webpage database
            update_db_portfolio()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('portfolio'))
        else:
            ## use pcb to debug django in console
            # pdb.set_trace()
            print(form.errors)

    # If this is a GET (or any other method) create the default form.
    else:
        form = PortfolioEditForm(ticker=model.ticker,
                                 long_name=model.long_name,
                                 instrument=model.instrument,
                                 sector=model.sector,
                                 industry=model.industry,
                                 price=model.price,
                                 currency=model.currency,
                                 quantity=model.quantity,
                                 timestamp=model.timestamp,
                                 action=model.action,
                                 account=model.account)

    context = {
        'form': form,
        'model': 'Trade'
    }

    return render(request, 'portfolio/model_edit.html', context)


def historyEditView(request):
    """View function for editing trade history."""

    # unpack the get request to retrieve ticker that we are editing
    id = [*request.GET.keys()][0]

    # get the model from the db
    model, created = TradeHistory.objects.get_or_create(pk=id)

    # If this is a POST request then process the Form data
    if request.method == 'POST':
        # Create a form instance and populate it with data from the request (binding):
        form = TradeInputForm(request.POST, instance=model)

        # Check if the form is valid:
        if form.is_valid():
            # update trade history
            form.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('orderHistory'))
        else:
            ## use pcb to debug django in console
            # pdb.set_trace()
            print(form.errors)

    # If this is a GET (or any other method) create the default form.
    else:
        form = HistoryEditForm(ticker=model.ticker,
                               long_name=model.long_name,
                               instrument=model.instrument,
                               sector=model.sector,
                               industry=model.industry,
                               price=model.price,
                               currency=model.currency,
                               quantity=model.quantity,
                               timestamp=model.timestamp,
                               action=model.action,
                               account=model.account,
                               fee=model.fee,
                               id=model.id)

    context = {
        'form': form,
        'model': 'TradeHistory'
    }

    return render(request, 'portfolio/model_edit.html', context)


def accountsEditView(request):
    """View function for editing Account balances"""

    # unpack the get request to retrieve ticker that we are editing
    account = [*request.GET.keys()][0]
    # get the model from the db
    model, created = Accounts.objects.get_or_create(pk=account)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = AccountInputForm(request.POST, instance=model)

        # Check if the form is valid:
        if form.is_valid():
            form.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('accounts'))
        else:
            ## use pcb to debug django in console
            # pdb.set_trace()
            print(form.errors)

    # If this is a GET (or any other method) create the default form.
    else:
        form = AccountEditForm(account=model.account,
                               broker=model.broker,
                               ccy=model.ccy,
                               balance=model.balance)

    context = {
        'form': form,
        'model': 'Accounts'
    }

    return render(request, 'portfolio/model_edit.html', context)


# template view for market data charts
class MarketDataCharts(TemplateView):
    template_name = 'market_data.html'

    def get_context_data(self, **kwargs):
        context = super(MarketDataCharts, self).get_context_data(**kwargs)
        # add charts to context using defined functions for generating
        context['map_chart'] = get_map_chart()
        context['volatility_chart'] = get_volatility_chart()
        context['market_chart'] = get_market_chart()
        context['backtest_chart'] = get_backtest_chart()
        context['market_backtest_chart'] = get_market_backtest_chart()
        context['market_reversion_chart'] = get_market_reversion_chart()

        #pdb.set_trace()

        return context


# template view for market crypto data charts
class CryptoMarketDataCharts(TemplateView):
    template_name = 'crypto_market_data.html'

    def get_context_data(self, **kwargs):
        context = super(CryptoMarketDataCharts, self).get_context_data(**kwargs)
        # add charts to context using defined functions for generating
        charts = get_crypto_charts()
        # context is a dict that we assign a key and a value, thus in theory could pass anything realy
        context['charts'] = charts
        # pdb.set_trace()
        return context


def deleteRecord(request):
    """View function for deleting line items """

    # unpack the get request to retrieve ticker that we are editing
    id = [*request.GET.keys()][0]
    model_type = request.GET[id]

    if model_type == 'portfolio':
        base_page = 'portfolio'
        model, created = Trade.objects.get_or_create(pk=id)
    elif model_type == 'Accounts':
        base_page = 'accounts'
        model, created = Accounts.objects.get_or_create(pk=id)
    elif model_type == 'history':
        base_page = 'orderHistory'
        model, created = TradeHistory.objects.get_or_create(pk=id)
    else:
        raise ValueError('delete type "%s" not recognised' % model_type)

    model.delete()

    if model_type == 'portfolio':
        # update mongo database to reflect data in webpage database
        update_db_portfolio()

    return HttpResponseRedirect(reverse(base_page))

