"""PJM_webApp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from portfolio import views
from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
]

urlpatterns += [
    # change this to summary later on
    path('', RedirectView.as_view(url='/login/')),
    path('portfolio/', views.TradeListView.as_view(), name='portfolio'),
    path('accounts/', views.AccountListView.as_view(), name='accounts'),
    path('order history/', views.TradeHistoryListView.as_view(), name='orderHistory'),
    path('stock market analysis/', views.MarketDataCharts.as_view(), name='marketData'),
    path('crypto market analysis/', views.CryptoMarketDataCharts.as_view(), name='cryptoMarketData')
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += [
    path('login/', views.loginView, name='login'),
    path('new account/', views.createUserView, name='createUser'),
    path('input trade/', views.tradeInputView, name='tradeInput'),
    path('input account/', views.accountInputView, name='accountInput'),
    path('edit portfolio/', views.portfolioEditView, name='portfolioEdit'),
    path('edit history/', views.historyEditView, name='historyEdit'),
    path('edit accounts/', views.accountsEditView, name='accountsEdit'),
    path('delete entry/', views.deleteRecord, name='deleteView'),
]

