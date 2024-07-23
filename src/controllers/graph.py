import io
import base64
import locale
import matplotlib.pyplot as plt

from flask import abort, jsonify, request, Blueprint
from Service.generate_sales_graph import generatesalesgraph

from flask import request, abort, Response, Blueprint
from bokeh.plotting import figure, output_file, show
from bokeh.io import export_png
from bokeh.models import PrintfTickFormatter, LabelSet, ColumnDataSource
from io import BytesIO
from decimal import Decimal

locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8') # Define a localidade para português brasileiro

def calculate_figure_size(num_items):
  # Ajusta o tamanho com base no número de itens
  width = 10
  height = max(6, num_items * 0.5)  # Ajusta a altura com base na quantidade de dados
  return (width, height)

REQUEST_API = Blueprint('graph', __name__)

@REQUEST_API.route('/fetch_sales', methods=['GET'])
def fetch_sales(): 
  dt_inicial = request.args.get('dt_inicial')
  dt_final = request.args.get('dt_final')
  idstatus = request.args.get('idstatus')
  idcategoria = request.args.get('idcategoria')
  idusuario = request.args.get('idusuario')

  if not dt_inicial and not dt_final and not idstatus and not idcategoria and not idusuario:
    abort(400, description="Parâmetros insuficientes")

  response = generatesalesgraph(dt_inicial, dt_final, idstatus, idcategoria, idusuario)

  produtos = []
  quantidade = []
  valor_produto = []
  valor_formatado = []


  for item in response:
    descricao = item['descricao']
    modelo = item['modelo']
    qtd = int(Decimal(item['qtd']))
    valor = float(Decimal(item['valor']))

    produtos.append(descricao + ' - ' + modelo)
    quantidade.append(qtd)
    valor_produto.append(valor)

    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
    valor_formatado.append(locale.currency(valor, grouping=True))


  # Calcular a soma total dos valores
  total_valor = sum(valor_produto)

  # Ajustar o tamanho da figura com base no número de itens
  num_items = len(produtos)
  figsize = (12, num_items * 0.5)  # Ajustar o tamanho da figura conforme o número de itens

  # Criar o gráfico com Matplotlib
  fig, ax = plt.subplots(figsize=figsize)

  # Adicionar as barras horizontais
  bars = ax.barh(produtos, valor_produto, color='blue')

  # Adicionar rótulos ao centro das barras
  for bar in bars:
    width = bar.get_width()
    label = f'{width:.2f}'  # Texto com a quantidade formatado
    ax.text(width / 2, bar.get_y() + bar.get_height() / 2, label,
            ha='center', va='center', color='white', fontsize=10)

  # Adicionar rótulos com quantidade à direita das barras
  for i, (qtd, valor) in enumerate(zip(quantidade, valor_produto)):
    ax.text(valor + max(valor_produto) * 0.02, i, f'{qtd}', va='center', color='black', fontsize=10)

  # Configuração dos eixos e título
  ax.set_xlabel('Valor')
  ax.set_ylabel('Produtos')
  ax.set_title('Quantidade Vendida dos Produtos')

  # Ajustar o espaço das margens
  plt.tight_layout()

  # Salvando o gráfico em um buffer em memória
  buf = io.BytesIO()
  plt.savefig(buf, format='png', bbox_inches='tight')  # bbox_inches='tight' para ajustar o layout
  buf.seek(0)

  # Convertendo o buffer PNG para base64
  img_base64 = base64.b64encode(buf.read()).decode('utf-8')

  # Fechando o gráfico
  plt.close(fig)

  # Retornando a base64 como resposta JSON
  return jsonify({'image': img_base64})

@REQUEST_API.route('/get-all', methods=['GET'])
def get(): 
  return "retorna muitas coias"




