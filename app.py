import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import datetime
import yfinance as yf


from ibov_utils import conserta_setores, criar_codigo_sa, carrega_data_tickers

st.title("Dashboard IBOV v2")

ibov = pd.read_csv('composicao_ibov.csv', sep=';', encoding='ISO-8859-1',
            engine='python', skipfooter=2, thousands='.',
            decimal=',', header=1, index_col=False)
ibov["SubSetor"] = ibov.Setor.apply(lambda s : s[s.rfind("/")+1:].strip())
ibov["Setor"] = ibov.Setor.apply(lambda s : s[:s.rfind("/")].strip())
ibov["Setor"] = ibov.Setor.apply(conserta_setores)
ibov['Código_SA'] = ibov['Código'].apply(criar_codigo_sa)

ibov_atual = yf.Ticker('^BVSP').info['regularMarketPrice']
ibov_previa = yf.Ticker('^BVSP').info['previousClose']
var_ibov = 100 * (ibov_atual/ibov_previa - 1)

smll_atual = yf.Ticker('SMAL11.SA').info['regularMarketPrice']
smll_previa = yf.Ticker('SMAL11.SA').info['previousClose']
var_smll = 100 * (smll_atual/smll_previa - 1)

spx_atual = yf.Ticker('^SPX').info['regularMarketPrice']
spx_previa = yf.Ticker('^SPX').info['previousClose']
var_spx = 100*(spx_atual/spx_previa - 1)

btc_atual = yf.Ticker('BTC-USD').info['regularMarketPrice']
btc_previa = yf.Ticker('BTC-USD').info['previousClose']
var_btc = 100*(btc_atual/btc_previa - 1)

data_tickers = carrega_data_tickers(ibov['Código_SA'].to_list())


@st.cache(allow_output_mutation=True)
def capturar_dt_atualizacao():
    return datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")


@st.cache(allow_output_mutation=True)
def captura_preco_atual(ticker, data_tickers=data_tickers):
    acao = data_tickers.tickers[ticker]
    return acao.info['currentPrice']


@st.cache(allow_output_mutation=True)
def captura_variacao(ticker, data_tickers=data_tickers):
    acao = data_tickers.tickers[ticker]
    return 100*((acao.info['currentPrice']/acao.info['previousClose'])-1)


ibov['Preco']=ibov['Código_SA'].apply(captura_preco_atual)
ibov['Variacao']=ibov['Código_SA'].apply(captura_variacao)

def plot_sunburst():
    fig = px.sunburst(data_frame=ibov, path= ['Setor', 'SubSetor', 'Código'],
                      values='Part. (%)', height=700)
    fig.update_traces(textfont_color='white', textfont_size=14,
                      hovertemplate='<b>%{label}:</b> %{value:.2f}%')
    return fig


def plot_treemap():
    condition = [ibov["Variacao"] > 0,
                 ibov["Variacao"] == 0,
                 ibov["Variacao"] < 0]

    choices = ['A', 'B', 'C']
    ibov['Condition'] = np.select(condition,choices,default='D')
    ibov.sort_values('Variacao', inplace=True)
    fig = px.treemap(ibov, path=['Setor', 'SubSetor', 'Código'],
                     values='Part. (%)',
                     color='Condition',
                     color_discrete_map={'(?)': '#AED6F1 ', 'A': "#19BD1B",
                                     'B': "#C0C0C0",
                                     'C': "#DC3714",
                                     'D': '#AB63FA'},
                     custom_data=['Variacao', 'Preco', 'Setor', 'SubSetor'],
                     height=800)

    variacoes = ibov.Variacao.tolist()

    fig.update_traces(textinfo="label",
                      textposition="middle center",
                      hovertemplate='%{label}<br>%{customdata[0]:.2f}%' +
                                    '%{customdata[2]}/%{customdata[3]}',
                      texttemplate='%{label}<br>%{customdata[0]:.2f}%<br>' +
                                   'R$ %{customdata[1]:.2f}')
    fig.data[0]['textfont']['size'] = 14
    return fig

tab1, tab2, tab3, tab4 = st.tabs(["Índices", "Situação Ibov", "Composição Ibov", "Consulta Ticker"])

with tab1:
    col1, col2 = st.columns(2)
    col1.metric(label="IBOV", value=ibov_atual, delta="{:.2f}".format(var_ibov))
    col2.metric(label="SMALL11", value=smll_atual, delta="{:.2f}".format(var_smll))
    col3, col4 = st.columns(2)
    col3.metric(label="US500", value=ibov_previa, delta="{:.2f}".format(var_spx))
    col4.metric(label="Bitcoin", value=btc_previa, delta="{:.2f}".format(var_btc))

with tab2:
    st.plotly_chart(
        plot_treemap(), use_container_width=True)
    st.text("Informações atualizadas em " + capturar_dt_atualizacao())


with tab3:
    st.plotly_chart(
       plot_sunburst(), use_container_width=True)

with tab4:
    st.plotly_chart(
       plot_sunburst(), use_container_width=True)
