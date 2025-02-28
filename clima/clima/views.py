import requests
from bs4 import BeautifulSoup
from django.shortcuts import render

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Clima
from .serializers import ClimaSerializer
import requests
from bs4 import BeautifulSoup


from rest_framework.response import Response
from rest_framework.decorators import api_view
import requests
from bs4 import BeautifulSoup
from .models import Cidade

@api_view(['GET'])
def obter_dados_clima(request, cidade_nome):
    try:
        cidade = Cidade.objects.get(nome__iexact=cidade_nome)  # Busca a cidade no BD
        headers = {'User-Agent': 'Mozilla/5.0'}

        url_previsao = f"https://www.climatempo.com.br/previsao-do-tempo/cidade/{cidade.codigo_climatempo}/{cidade.nome.lower().replace(' ', '')}-rj"
        url_agora = f"https://www.climatempo.com.br/previsao-do-tempo/agora/cidade/{cidade.codigo_climatempo}/{cidade.nome.lower().replace(' ', '')}-rj"
        url_precipitacao = cidade.link_precipitacao

        context = {}

        # Fonte 1: Temperatura
        try:
            response = requests.get(url_previsao, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            temp_min = soup.find(id='min-temp-1')
            temp_max = soup.find(id='max-temp-1')

            context['temp_min'] = temp_min.text if temp_min else "Não disponível"
            context['temp_max'] = temp_max.text if temp_max else "Não disponível"
        except Exception as e:
            context['temp_min'] = context['temp_max'] = "Erro ao obter temperatura"

        # Fonte 2: Sensação térmica
        try:
            response = requests.get(url_agora, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            sensacao_element = soup.find(class_='no-gutters -gray _flex _justify-center _margin-t-20 _padding-b-20 _border-b-light-1')
            context['sensacao'] = sensacao_element.text if sensacao_element else "Não disponível"
        except Exception as e:
            context['sensacao'] = "Erro ao obter sensação térmica"

        # Fonte 3: Precipitação
        try:
            response = requests.get(url_precipitacao, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            chuva_element = soup.find(class_='precipitationValue')
            context['chuva'] = chuva_element.find('span').text.strip() if chuva_element else "Precipitação não encontrada"
        except Exception as e:
            context['chuva'] = "Erro ao obter precipitação"

        return Response(context)

    except Cidade.DoesNotExist:
        return Response({'error': 'Cidade não encontrada'}, status=404)


class ClimaViewSet(viewsets.ModelViewSet):
    queryset = Clima.objects.all()
    serializer_class = ClimaSerializer

    @action(detail=True, methods=['get'])
    def atualizar(self, request, pk=None):
        """Endpoint para atualizar os dados climáticos da cidade"""
        try:
            clima = self.get_object()
            headers = {'User-Agent': 'Mozilla/5.0'}

            url_previsao = f"https://www.climatempo.com.br/previsao-do-tempo/cidade/{clima.id}/{clima.cidade.lower().replace(' ', '')}-rj"
            url_agora = f"https://www.climatempo.com.br/previsao-do-tempo/agora/cidade/{clima.id}/{clima.cidade.lower().replace(' ', '')}-rj"
            url_precipitacao = f"https://tempo.clic.com.br/rj/{clima.cidade.lower().replace(' ', '-')}"

            # Fonte 1: Temperatura
            response = requests.get(url_previsao, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            temp_min = soup.find(id='min-temp-1')
            temp_max = soup.find(id='max-temp-1')

            clima.temp_min = temp_min.text if temp_min else "Não disponível"
            clima.temp_max = temp_max.text if temp_max else "Não disponível"

            # Fonte 2: Sensação térmica
            response = requests.get(url_agora, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            sensacao_element = soup.find(class_='no-gutters -gray _flex _justify-center _margin-t-20 _padding-b-20 _border-b-light-1')
            clima.sensacao = sensacao_element.text if sensacao_element else "Não disponível"

            # Fonte 3: Precipitação
            response = requests.get(url_precipitacao, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            chuva_element = soup.find(class_='precipitationValue')
            clima.chuva = chuva_element.find('span').text.strip() if chuva_element else "Precipitação não encontrada"

            clima.save()
            return Response({'status': 'Dados atualizados!', 'data': ClimaSerializer(clima).data})

        except Exception as e:
            return Response({'error': str(e)}, status=400)



def pegar_dados_clima(request):
    context = {}
    headers = {'User-Agent': 'Mozilla/5.0'}

    # Fonte 1: Temperatura
    try:
        url = 'http://climatempo.com.br/previsao-do-tempo/cidade/321/riodejaneiro-rj'
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        temp_min1 = soup.find(id='min-temp-1')
        temp_max1 = soup.find(id='max-temp-1')
        
        context['temp_min'] = temp_min1.text if temp_min1 else "Não disponível"
        context['temp_max'] = temp_max1.text if temp_max1 else "Não disponível"
    except Exception as e:
        print(f"Erro ao buscar temperatura: {e}")
        context['temp_min'] = context['temp_max'] = "Erro ao obter dados"

    # Fonte 2: Sensação térmica
    try:
        fonte2 = 'https://www.climatempo.com.br/previsao-do-tempo/agora/cidade/321/riodejaneiro-rj'
        response = requests.get(fonte2, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        sensacao_element = soup.find(class_='no-gutters -gray _flex _justify-center _margin-t-20 _padding-b-20 _border-b-light-1')
        context['sensacao'] = sensacao_element.text if sensacao_element else "Não disponível"
    except Exception as e:
        print(f"Erro ao buscar sensação térmica: {e}")
        context['sensacao'] = "Erro ao obter dados"

    # Fonte 3: Precipitação
    try:
        fonte3 = requests.get('https://tempo.clic.com.br/rj/rio-dejaneiro', headers=headers)
        fonte3.raise_for_status()
        soup = BeautifulSoup(fonte3.text, 'html.parser')
        chuva_element = soup.find(class_='precipitationValue')
        context['chuva'] = chuva_element.find('span').text.strip() if chuva_element else "Precipitação não encontrada"
    except Exception as e:
        print(f"Erro ao buscar precipitação: {e}")
        context['chuva'] = "Erro ao obter dados"

    # Fonte 4: Dados de saúde
    try:
        response = requests.get(fonte2, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        card_health = soup.find('div', class_='card -no-top')
        health_items = card_health.find_all('li', class_='item') if card_health else []
        dados_saude = {}
        for item in health_items:
            titulo = item.find('p', class_='title')
            valor = item.find('p', class_='value')
            if titulo and valor:
                dados_saude[titulo.get_text(strip=True)] = valor.get_text(strip=True)
        context['dados_saude'] = dados_saude if dados_saude else "Dados de saúde não encontrados"
    except Exception as e:
        print(f"Erro ao buscar dados de saúde: {e}")
        context['dados_saude'] = "Erro ao obter dados"

    # Fonte 5: Tabela de deslizamentos
    try:
        fonte5 = 'https://sistema-alerta-rio.com.br/upload/SituacaoAtual.html'
        response = requests.get(fonte5, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        tabela = soup.find('table', width="100%")
        tabela_dados = []
        if tabela:
            rows = tabela.find_all('tr')
            for row in rows:
                cols = row.find_all('th')
                if len(cols) == 2:
                    regiao = cols[0].text.strip()
                    probabilidade = cols[1].find('font').text.strip() if cols[1].find('font') else "Não disponível"
                    tabela_dados.append([regiao, probabilidade])
        context['tabela_dados'] = tabela_dados if tabela_dados else "Tabela de deslizamento não encontrada"
    except Exception as e:
        print(f"Erro ao buscar dados de deslizamento: {e}")
        context['tabela_dados'] = "Erro ao obter dados"

    
    return render(request, 'html/home.html', context)

def pegar_dados_clima_belford_roxo(request):
    context = {}
    headers = {'User-Agent': 'Mozilla/5.0'}

    # Fonte 1: Temperatura
    try:
        url = 'https://www.climatempo.com.br/previsao-do-tempo/cidade/289/belfordroxo-rj'
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        temp_min1 = soup.find(id='min-temp-1')
        temp_max1 = soup.find(id='max-temp-1')
        
        context['temp_min'] = temp_min1.text if temp_min1 else "Não disponível"
        context['temp_max'] = temp_max1.text if temp_max1 else "Não disponível"
        print(f"Belford Roxo - Temp Mín: {context['temp_min']}, Temp Máx: {context['temp_max']}")
    except Exception as e:
        print(f"Erro ao buscar temperatura para Belford Roxo: {e}")
        context['temp_min'] = context['temp_max'] = "Erro ao obter dados"

    # Fonte 2: Sensação térmica
    try:
        fonte2 = 'https://www.climatempo.com.br/previsao-do-tempo/agora/cidade/289/belfordroxo-rj'
        response = requests.get(fonte2, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        sensacao_element = soup.find(class_='no-gutters -gray _flex _justify-center _margin-t-20 _padding-b-20 _border-b-light-1')
        context['sensacao'] = sensacao_element.text if sensacao_element else "Não disponível"
        print(f"Belford Roxo - Sensação térmica: {context['sensacao']}")
    except Exception as e:
        print(f"Erro ao buscar sensação térmica para Belford Roxo: {e}")
        context['sensacao'] = "Erro ao obter dados"

    # Fonte 3: Precipitação
    try:
        fonte3 = requests.get('https://tempo.clic.com.br/rj/belford-roxo', headers=headers)
        fonte3.raise_for_status()
        soup = BeautifulSoup(fonte3.text, 'html.parser')
        chuva_element = soup.find(class_='precipitationValue')
        context['chuva'] = chuva_element.find('span').text.strip() if chuva_element else "Precipitação não encontrada"
        print(f"Belford Roxo - Precipitação: {context['chuva']}")
    except Exception as e:
        print(f"Erro ao buscar precipitação para Belford Roxo: {e}")
        context['chuva'] = "Erro ao obter dados"

    # Fonte 4: Dados de saúde
    try:
        response = requests.get(fonte2, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        card_health = soup.find('div', class_='card -no-top')
        health_items = card_health.find_all('li', class_='item') if card_health else []
        dados_saude = {}
        for item in health_items:
            titulo = item.find('p', class_='title')
            valor = item.find('p', class_='value')
            if titulo and valor:
                dados_saude[titulo.get_text(strip=True)] = valor.get_text(strip=True)
        context['dados_saude'] = dados_saude if dados_saude else "Dados de saúde não encontrados"
        print(f"Belford Roxo - Dados de saúde: {context['dados_saude']}")
    except Exception as e:
        print(f"Erro ao buscar dados de saúde para Belford Roxo: {e}")
        context['dados_saude'] = "Erro ao obter dados"

    return render(request, 'html/home.html', context)


def pegar_dados_clima_angra_reis(request):
    context = {}
    headers = {'User-Agent': 'Mozilla/5.0'}

    # Fonte 1: Temperatura
    try:
        url = 'https://www.climatempo.com.br/previsao-do-tempo/cidade/769/angradosreis-rj'
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        temp_min1 = soup.find(id='min-temp-1')
        temp_max1 = soup.find(id='max-temp-1')
        
        context['temp_min'] = temp_min1.text if temp_min1 else "Não disponível"
        context['temp_max'] = temp_max1.text if temp_max1 else "Não disponível"
        print(f"Angra dos Reis - Temp Mín: {context['temp_min']}, Temp Máx: {context['temp_max']}")
    except Exception as e:
        print(f"Erro ao buscar temperatura para Angra dos Reis: {e}")
        context['temp_min'] = context['temp_max'] = "Erro ao obter dados"

    # Fonte 2: Sensação térmica
    try:
        fonte2 = 'https://www.climatempo.com.br/previsao-do-tempo/agora/cidade/769/angradosreis-rj'
        response = requests.get(fonte2, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        sensacao_element = soup.find(class_='no-gutters -gray _flex _justify-center _margin-t-20 _padding-b-20 _border-b-light-1')
        context['sensacao'] = sensacao_element.text if sensacao_element else "Não disponível"
        print(f"Angra dos Reis - Sensação térmica: {context['sensacao']}")
    except Exception as e:
        print(f"Erro ao buscar sensação térmica para Angra dos Reis: {e}")
        context['sensacao'] = "Erro ao obter dados"

    # Fonte 3: Precipitação
    try:
        fonte3 = requests.get('https://tempo.clic.com.br/rj/angra-dos-reis', headers=headers)
        fonte3.raise_for_status()
        soup = BeautifulSoup(fonte3.text, 'html.parser')
        chuva_element = soup.find(class_='precipitationValue')
        context['chuva'] = chuva_element.find('span').text.strip() if chuva_element else "Precipitação não encontrada"
        print(f"Angra dos Reis - Precipitação: {context['chuva']}")
    except Exception as e:
        print(f"Erro ao buscar precipitação para Angra dos Reis: {e}")
        context['chuva'] = "Erro ao obter dados"

    # Fonte 4: Dados de saúde
    try:
        response = requests.get(fonte2, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        card_health = soup.find('div', class_='card -no-top')
        health_items = card_health.find_all('li', class_='item') if card_health else []
        dados_saude = {}
        for item in health_items:
            titulo = item.find('p', class_='title')
            valor = item.find('p', class_='value')
            if titulo and valor:
                dados_saude[titulo.get_text(strip=True)] = valor.get_text(strip=True)
        context['dados_saude'] = dados_saude if dados_saude else "Dados de saúde não encontrados"
        print(f"Angra dos Reis - Dados de saúde: {context['dados_saude']}")
    except Exception as e:
        print(f"Erro ao buscar dados de saúde para Belford Roxo: {e}")
        context['dados_saude'] = "Erro ao obter dados"

    return render(request, 'html/home.html', context)

def pegar_dados_clima_araruama(request):
    context = {}
    headers = {'User-Agent': 'Mozilla/5.0'}

    # Fonte 1: Temperatura
    try:
        url = 'https://www.climatempo.com.br/previsao-do-tempo/cidade/285/araruama-rj'
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        temp_min1 = soup.find(id='min-temp-1')
        temp_max1 = soup.find(id='max-temp-1')
        
        context['temp_min'] = temp_min1.text if temp_min1 else "Não disponível"
        context['temp_max'] = temp_max1.text if temp_max1 else "Não disponível"
        print(f"Araruama - Temp Mín: {context['temp_min']}, Temp Máx: {context['temp_max']}")
    except Exception as e:
        print(f"Erro ao buscar temperatura para Araruama: {e}")
        context['temp_min'] = context['temp_max'] = "Erro ao obter dados"

    # Fonte 2: Sensação térmica
    try:
        fonte2 = 'https://www.climatempo.com.br/previsao-do-tempo/agora/cidade/285/araruama-rj'
        response = requests.get(fonte2, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        sensacao_element = soup.find(class_='no-gutters -gray _flex _justify-center _margin-t-20 _padding-b-20 _border-b-light-1')
        context['sensacao'] = sensacao_element.text if sensacao_element else "Não disponível"
        print(f"Araruama - Sensação térmica: {context['sensacao']}")
    except Exception as e:
        print(f"Erro ao buscar sensação térmica para Araruama: {e}")
        context['sensacao'] = "Erro ao obter dados"

    # Fonte 3: Precipitação
    try:
        fonte3 = requests.get('https://tempo.clic.com.br/rj/araruama', headers=headers)
        fonte3.raise_for_status()
        soup = BeautifulSoup(fonte3.text, 'html.parser')
        chuva_element = soup.find(class_='precipitationValue')
        context['chuva'] = chuva_element.find('span').text.strip() if chuva_element else "Precipitação não encontrada"
        print(f"Araruama - Precipitação: {context['chuva']}")
    except Exception as e:
        print(f"Erro ao buscar precipitação para Araruama: {e}")
        context['chuva'] = "Erro ao obter dados"

    # Fonte 4: Dados de saúde
    try:
        response = requests.get(fonte2, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        card_health = soup.find('div', class_='card -no-top')
        health_items = card_health.find_all('li', class_='item') if card_health else []
        dados_saude = {}
        for item in health_items:
            titulo = item.find('p', class_='title')
            valor = item.find('p', class_='value')
            if titulo and valor:
                dados_saude[titulo.get_text(strip=True)] = valor.get_text(strip=True)
        context['dados_saude'] = dados_saude if dados_saude else "Dados de saúde não encontrados"
        print(f"Araruama - Dados de saúde: {context['dados_saude']}")
    except Exception as e:
        print(f"Erro ao buscar dados de saúde para Araruama: {e}")
        context['dados_saude'] = "Erro ao obter dados"

    return render(request, 'html/home.html', context)




def pegar_dados_clima_arraial_do_cabo(request):
    context = {}
    headers = {'User-Agent': 'Mozilla/5.0'}

    # Fonte 1: Temperatura
    try:
        url = 'https://www.climatempo.com.br/previsao-do-tempo/cidade/770/arraialdocabo-rj'
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        temp_min1 = soup.find(id='min-temp-1')
        temp_max1 = soup.find(id='max-temp-1')

        context['temp_min'] = temp_min1.text if temp_min1 else "Não disponível"
        context['temp_max'] = temp_max1.text if temp_max1 else "Não disponível"
        print(f"Arraial do Cabo - Temp Mín: {context['temp_min']}, Temp Máx: {context['temp_max']}")
    except Exception as e:
        print(f"Erro ao buscar temperatura para Arraial do Cabo: {e}")
        context['temp_min'] = context['temp_max'] = "Erro ao obter dados"

    # Fonte 2: Sensação térmica
    try:
        fonte2 = 'https://www.climatempo.com.br/previsao-do-tempo/agora/cidade/770/arraialdocabo-rj'
        response = requests.get(fonte2, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        sensacao_element = soup.find(class_='no-gutters -gray _flex _justify-center _margin-t-20 _padding-b-20 _border-b-light-1')
        context['sensacao'] = sensacao_element.text if sensacao_element else "Não disponível"
        print(f"Arraial do Cabo - Sensação térmica: {context['sensacao']}")
    except Exception as e:
        print(f"Erro ao buscar sensação térmica para Arraial do Cabo: {e}")
        context['sensacao'] = "Erro ao obter dados"

    # Fonte 3: Precipitação
    try:
        fonte3 = requests.get('https://tempo.clic.com.br/rj/arraial-do-cabo', headers=headers)
        fonte3.raise_for_status()
        soup = BeautifulSoup(fonte3.text, 'html.parser')
        chuva_element = soup.find(class_='precipitationValue')
        context['chuva'] = chuva_element.find('span').text.strip() if chuva_element else "Precipitação não encontrada"
        print(f"Arraial do Cabo - Precipitação: {context['chuva']}")
    except Exception as e:
        print(f"Erro ao buscar precipitação para Arraial do Cabo: {e}")
        context['chuva'] = "Erro ao obter dados"

    return render(request, 'html/home.html', context)


