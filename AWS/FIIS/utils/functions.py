import json
import pandas as pd
import re
from decimal import Decimal
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen

def trata_html(input):
   return " ".join(input.split()).replace('> <', '><')


def create_bsoup_object(url):
    headers = {'User-Agent': 'xxxx'}
    req = Request(url, headers = headers)
    response = urlopen(req)
    html = response.read()
    html = html.decode('utf-8')
    html = trata_html(html)
    ## create BeautifulSoup object
    soup = BeautifulSoup(html, 'html.parser')
    return soup


def get_tickers(soup):
    tickers = soup.findAll('div', {'class': 'tickerBox__title', 'data-element':'ticker-box-title'})
    codigos = []
    
    for ticker in tickers:
        codigos.append(ticker.get_text().lower())
    
    return codigos


# def create_fiis_dataframe(tickers):
#     cards = []
#     for ticker in tickers:
#         print(ticker.upper())
#         url = 'https://fiis.com.br/' + ticker
#         soup = create_bsoup_object(url)
#         items = soup.find_all(class_ = 'value')
#         infos = []
#         card = {}
#         for item in items:
#             infos.append(item.get_text())
#         card['ticker'] = ticker.upper()
#         admin = soup.findAll("div", {"class": "text-wrapper"})
#         card['administrador'] = re.sub("ADMINISTRADOR|[0-9].*[0-9]", "", admin[0].get_text())
#         card['dividend_yield'] = infos[0]
#         card['ultimo_rendimento'] = infos[1]
#         card['patrimonio_liquido'] = infos[2]
#         card['valor_patrimonial_por_cota'] = infos[3]
#         card['telefone'] = infos[4]
#         card['email'] = infos[5]
#         card['site'] = infos[6]
#         card['name'] = infos[7]
#         card['tipo_FII'] = infos[8]
#         card['tipo_ANBIMA'] = infos[9]
#         card['registro_CVM'] = infos[10]
#         card['numero_cotas'] = infos[11]
#         card['numero_cotistas'] = infos[12]
#         card['CNPJ'] = infos[13]
#         card['cotacao'] = infos[14]
#         card['min_52_weeks'] = infos[15]
#         card['max_52_weeks'] = infos[16]
#         card['return_12_months'] = infos[17]
            
#         cards.append(card)
        
#     ## Create dataframe with the results
#     dataset = pd.DataFrame(cards)
#     return dataset

def create_fiis_dataframe(tickers):
    cards = []
    for ticker in tickers:
        print(ticker.upper())
        url = 'https://fiis.com.br/' + ticker
        soup = create_bsoup_object(url)
        items = soup.findAll('span', {'class': 'value'})
        infos = []
        card = {}
        for item in items:
            infos.append(item.get_text())
        card['ticker'] = ticker.upper()
        card['cotacao'] = infos[0]
        card['min_52_weeks'] = infos[1]
        card['max_52_weeks'] = infos[2]

            
        cards.append(card)
        
    ## Create dataframe with the results
    dataset = pd.DataFrame(cards)
    return dataset

def break_tipo_FII(dataset):
    dataset["tipo"] = dataset['tipo_FII'].str.replace(":.*", "", regex = True).str.strip()
    dataset["subtipo"] = dataset['tipo_FII'].str.replace(".*:", "", regex = True).str.strip()
    dataset = dataset.drop(['tipo_FII'], axis='columns')
    return dataset


def create_ifix_dataframe(URL):
    soup = create_bsoup_object(URL)
    ifix_tickers = soup.findAll('tr')[1:]
    cards = []
    for ifix_ticker in ifix_tickers:
        card={}
        card['ticker'] = ifix_ticker.find("button", {'class':'follow-btn'})['data-ticker']
        card['peso'] = ifix_ticker.findAll("td")[0].get_text()
        cards.append(card)
    dataset = pd.DataFrame(cards)
    return dataset


def batch_write(dynamodb, table_name, items, overwrite_by_pkeys):
    """
    Batch write items to given table name
    """
       
    table = dynamodb.Table(table_name)
    
    with table.batch_writer(overwrite_by_pkeys=overwrite_by_pkeys) as batch:
        for item in items:
            #print(item)
            item = json.loads(json.dumps(item), parse_float=Decimal)
            batch.put_item(Item=item)
    return True