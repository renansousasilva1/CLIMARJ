from django.contrib import admin
from django.urls import path
from clima import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('dados-clima/', views.pegar_dados_clima, name='dados_clima'),
    path('dados-clima-belford-roxo/', views.pegar_dados_clima_belford_roxo, name='dados_clima_belford_roxo'),
    path('dados-clima-angra-dos-reis/', views.pegar_dados_clima_angra_reis, name='dados_clima_angra_dos_reis'),
    path('dados-clima-araruama/', views.pegar_dados_clima_araruama, name='dados_clima_araruama'),
    path('dados-clima-arraial-do-cabo/', views.pegar_dados_clima_arraial_do_cabo, name='dados_clima_arraial_do_cabo'),
    path('api/clima/<str:cidade_nome>/', views.obter_dados_clima, name='obter_dados_clima'),  # Corrigido para views.obter_dados_clima
]

