import io
import locale
import openpyxl

from decimal import Decimal
from datetime import datetime
from flask import abort, request, make_response, Blueprint
from openpyxl.chart import BarChart, Reference
from openpyxl.chart.label import DataLabel, DataLabelList

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
    chart_sheet.title = 'Gráficos'

    # Segunda aba para os dados
    data_sheet = workbook.create_sheet(title='Dados de Vendas')

    # Escrever o cabeçalho do XLSX na segunda aba
    data_sheet.append(['Produto', 'Quantidade', 'Valor', 'Valor Formatado'])

    # Escrever os dados no XLSX na segunda aba
    for prod, qtd, val, val_fmt in zip(produtos, quantidade, valor_produto, valor_formatado):
        data_sheet.append([prod, qtd, val, val_fmt])

    # Adicionar gráfico de barras para a quantidade
    chart_qtd = BarChart()
    chart_qtd.type = "bar"
    chart_qtd.style = 11
    chart_qtd.shape = 4  # Estilo de barra

    categories_ref = Reference(data_sheet, min_col=1, min_row=2, max_row=len(produtos) + 1)
    qtd_ref = Reference(data_sheet, min_col=2, min_row=1, max_row=len(quantidade) + 1)

    chart_qtd.add_data(qtd_ref, titles_from_data=True)
    chart_qtd.set_categories(categories_ref)

    # Centralizar os rótulos no centro da barra
    for series in chart_qtd.series:
        series.dLbls = DataLabelList()
        series.dLbls.showVal = True
        series.dLbls.showCatName = False
        series.dLbls.dLblPos = 'outEnd'  # Posicionar no centro da barra

    chart_qtd.y_axis.majorGridlines = None

    # Adicionar a legenda
    chart_qtd.legend.position = "r"  # Posições possíveis: 'r' (direita), 't' (acima), 'l' (esquerda), 'b' (abaixo)

    # Ajustar tamanho do gráfico
    chart_qtd.width = 40  # Ajuste conforme necessário
    chart_qtd.height = 15  # Ajuste conforme necessário

    chart_qtd.barWidth = 15  # Ajustar a largura das barras para criar espaço extra
    chart_qtd.gapWidth = 100  # Ajustar o espaçamento entre as barras

    chart_sheet.add_chart(chart_qtd, "B2")

    # Adicionar gráfico de barras para o valor
    chart_valor = BarChart()
    chart_valor.type = "bar"
    chart_valor.style = 11
    chart_valor.shape = 4  # Estilo de barra

    valor_ref = Reference(data_sheet, min_col=3, min_row=1, max_row=len(valor_produto) + 1)

    chart_valor.add_data(valor_ref, titles_from_data=True)
    chart_valor.set_categories(categories_ref)

    # Centralizar os rótulos no centro da barra
    for series in chart_valor.series:
        series.dLbls = DataLabelList()
        series.dLbls.showVal = True
        series.dLbls.showCatName = False
        series.dLbls.dLblPos = 'outEnd'  # Posicionar no centro da barra

    chart_valor.y_axis.majorGridlines = None

    # Adicionar a legenda
    chart_valor.legend.position = "r"  # Posições possíveis: 'r' (direita), 't' (acima), 'l' (esquerda), 'b' (abaixo)

    # Ajustar tamanho do gráfico
    chart_valor.width = 40  # Ajuste conforme necessário
    chart_valor.height = 15  # Ajuste conforme necessário

    chart_valor.barWidth = 15  # Ajustar a largura das barras para criar espaço extra
    chart_valor.gapWidth = 100  # Ajustar o espaçamento entre as barras

    chart_sheet.add_chart(chart_valor, "T2")  # Ajustar a posição para não sobrepor o gráfico de quantidade

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
