import io
import locale
import openpyxl

from decimal import Decimal
from flask import abort, request, make_response, Blueprint
from openpyxl.chart import BarChart, Reference
from openpyxl.chart.label import DataLabel
from openpyxl.chart.label import DataLabelList

from Service.generate_sales_graph import generatesalesgraph

locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')  # Define a localidade para português brasileiro

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

  # Criar uma planilha Excel em memória
  workbook = openpyxl.Workbook()

  # Primeira aba para o gráfico
  chart_sheet = workbook.active
  chart_sheet.title = 'Gráfico de Vendas'

  # Segunda aba para os dados
  data_sheet = workbook.create_sheet(title='Dados de Vendas')

  # Escrever o cabeçalho do XLSX na segunda aba
  data_sheet.append(['Produto', 'Quantidade', 'Valor Formatado'])

  # Escrever os dados no XLSX na segunda aba
  for prod, qtd, val, val_fmt in zip(produtos, quantidade, valor_produto, valor_formatado):
    data_sheet.append([prod, qtd, val_fmt])

  # Adicionar gráfico de barras horizontais na primeira aba
  chart = BarChart()
  chart.type = "bar"
  chart.style = 10

  data = Reference(data_sheet, min_col=2, min_row=1, max_row=len(quantidade) + 1)
  categories = Reference(data_sheet, min_col=1, min_row=2, max_row=len(produtos) + 1)
  chart.add_data(data, titles_from_data=True)
  chart.set_categories(categories)
  
  # Centralizar os rótulos no centro da barra
  for series in chart.series:
    series.dLbls = DataLabelList()
    series.dLbls.showVal = True
    series.dLbls.showCatName = False
    series.dLbls.dLblPos = 'ctr'  # Posicionar no centro da barra

  chart.y_axis.majorGridlines = None

  # Adicionar a legenda
  chart.legend.position = "r"  # Posições possíveis: 'r' (direita), 't' (acima), 'l' (esquerda), 'b' (abaixo)

  # Ajustar tamanho do gráfico
  chart.width = 30  # Ajuste conforme necessário
  chart.height = 15  # Ajuste conforme necessário

  chart_sheet.add_chart(chart, "A1")

  # Remover grades vazias e ocultar linhas e colunas da planilha de gráficos
  chart_sheet.sheet_view.showGridLines = False

  # Salvar o arquivo XLSX em memória usando BytesIO
  output = io.BytesIO()
  workbook.save(output)
  xlsx_data = output.getvalue()
  output.close()

  # Criar um nome de arquivo com a data atual
  current_date = datetime.now().strftime('%d-%m-%Y')  # Formato: '26-07-2024'
  filename = f'Relatorio-Vendas {current_date}.xlsx'

  # Criar uma resposta Flask para download do arquivo XLSX
  response = make_response(xlsx_data)
  response.headers['Content-Disposition'] = f'attachment; filename={filename}'
  response.headers['Content-type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

  return response