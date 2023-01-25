import awswrangler as wr
import boto3
import datetime

import urllib.request as urllib_request
from urllib.error import URLError, HTTPError

from utils.helpers import *
from utils.functions import *

URL = 'https://fiis.com.br/lista-de-fundos-imobiliarios/'
soup = create_bsoup_object(URL)
tickers = get_tickers(soup)
dataset = create_fiis_dataframe(tickers[0:10])
COLUMNS_LIST = [
                #'ultimo_rendimento',
                #'valor_patrimonial_por_cota',
                #'numero_cotas',
                #'numero_cotistas',
                'cotacao',
                'min_52_weeks',
                'max_52_weeks']
dataset = convert_string_to_float(dataset, COLUMNS_LIST)


URL = 'https://fiis.com.br/ifix/'
df_ifix = create_ifix_dataframe(URL)
COLUMNS_LIST = ['peso']
df_ifix = convert_percentages_to_float(df_ifix, COLUMNS_LIST)
df_ifix['date'] = str(datetime.date.today())



wr.s3.to_parquet(path='s3://tee2/ifix/',
                 df = df_ifix,
                 dataset=True,
                 mode='overwrite')