import yfinance as yf
import streamlit as st


def conserta_setores(setor):
  if setor == "Cons N  Básico" or setor == "Cons N Cíclico": return "Consumo Não-Cíclico"
  if setor == "Financeiro e Outros" or setor == "Financ e Outros": return "Financeiro"
  else: return setor


def criar_codigo_sa(codigo):
    return codigo + '.SA'


@st.cache(allow_output_mutation=True)
def carrega_data_tickers(tickers_list):
    data_tickers = yf.Tickers(tickers_list)
    return data_tickers
