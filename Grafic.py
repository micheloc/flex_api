from bokeh.plotting import figure, output_file, show
from bokeh.models import PrintfTickFormatter, LabelSet, ColumnDataSource

# Dados de exemplo
produtos = ['Produto A', 'Produto B', 'Produto C', 'Produto D']
valores = [150, 200.45, 120, 180]  # Campo para valores
quantidades = [10, 5, 8, 7]       # Campo para quantidades

# Criando o gráfico
p = figure(y_range=produtos, height=350, title="Quantidade Vendida dos Produtos", toolbar_location=None, tools="")

# Adicionando barras horizontais
p.hbar(y=produtos, right=valores, height=0.4)

# Adicionando rótulos
p.yaxis.axis_label = "Produtos"
p.xaxis.formatter = PrintfTickFormatter(format="%.2f")  # Formata os valores com duas casas decimais
p.xgrid.grid_line_color = None
p.y_range.factors = produtos
p.x_range.start = 0

# Adicionando rótulos com a quantidade centralizados e cor branca
source = ColumnDataSource(data=dict(produtos=produtos, quantidades=quantidades, valores=valores))
labels = LabelSet(x='valores', y='produtos', text='quantidades', source=source, 
                  x_offset=-250, y_offset=-5, text_font_size='10pt', text_align='center', text_color='white')

p.add_layout(labels)

# Definindo o arquivo de saída e exibindo o gráfico
output_file("grafico_bokeh_horizontal_com_quantidades_centralizadas_e_cor_branca.html")
show(p)
