import streamlit as st 
import pandas as pd
import math
import numpy as np
import plotly.express as px
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta

st.set_page_config(layout='wide')



df = pd.read_excel('dados.xlsx')

media =df['Avaliação'].mean()
mediana= df['Avaliação'].median()
moda = df['Avaliação'].mode()[0]
desvio_padrao = df['Avaliação'].std()
coeficiente_variacao = (desvio_padrao / media) * 100

# Calcular a tendência (usando regressão linear)
X = df['Dia'].values.reshape(-1, 1)
y = df['Avaliação'].values
modelo = LinearRegression()
modelo.fit(X, y)
tendencia = modelo.coef_[0]

# Valores máximos e mínimos
valores_min = df['Avaliação'].min()
valores_max = df['Avaliação'].max()

data = {'Tipo': ['Máxima', 'Mínima'], 'Valor': [valores_max, valores_min]}
df_max_min = pd.DataFrame(data)

# Número de classes usando a regra de Sturges
num_classes = math.ceil(1 + math.log2(len(df)))

# Amplitude amostral
amplitude_amostral = valores_max - valores_min

# Amplitude de cada classe
amplitude_classe = amplitude_amostral / num_classes

# # Limites das classes
limites_classes = [(valores_min + i * amplitude_classe, valores_min + (i + 1) * amplitude_classe) for i in range(num_classes)]

# # Pontos médios das classes
pontos_medios = [(limite[0] + limite[1]) / 2 for limite in limites_classes]

# Contagem de valores por classe
contagens_classes = []
for limite in limites_classes:
    contagem = ((df['Avaliação'] >= limite[0]) & (df['Avaliação'] < limite[1])).sum()
    contagens_classes.append(contagem)

# DataFrame com limites de classe e contagens
df_classes = pd.DataFrame({
    'Classe': range(1, num_classes + 1),
    'Limite Inferior': [limite[0] for limite in limites_classes],
    'Limite Superior': [limite[1] for limite in limites_classes],
    'Contagem': contagens_classes
})

# Frequências
frequencia_por_avaliacao = df['Avaliação'].value_counts().sort_index()
total_observacoes = frequencia_por_avaliacao.sum()
frequencia_relativa_por_avaliacao = frequencia_por_avaliacao / total_observacoes
frequencia_relativa_percentual_por_avaliacao = (frequencia_relativa_por_avaliacao * 100).round(2)
frequencia_acumulada = frequencia_por_avaliacao.cumsum()

df_frequencias = pd.DataFrame({
    'Avaliação': frequencia_por_avaliacao.index,
    'F': frequencia_por_avaliacao.values,
    'FR': frequencia_relativa_por_avaliacao.values,
    'FR(%)': frequencia_relativa_percentual_por_avaliacao.values,
    'FA': frequencia_acumulada.values
})

df_limites_classes = pd.DataFrame(limites_classes, columns=['Limite Inferior', 'Limite Superior'])
df_limites_classes = df_limites_classes.round(2)
df_limites_classes['Ponto Médio'] = pd.Series(pontos_medios).round(2)

# Montagem da tela no Streamlit

# Barra lateral
st.sidebar.header("Dados")
st.sidebar.dataframe(df[['Data', 'Avaliação']])
st.sidebar.write(f"Amplitude Amostral: {amplitude_amostral}")
st.sidebar.write(f"Amplitude Classes: {amplitude_classe:.2f}")

# Estatísticas adicionais
st.sidebar.write(f"Desvio Padrão: {desvio_padrao:.2f}")
st.sidebar.write(f"Tendência (Inclinação): {tendencia:.2f}")
st.sidebar.write(f"Coeficiente de Variação: {coeficiente_variacao:.2f}")

# Gráfico de linhas dos dados gerais
fig_date = px.bar(df, y='Avaliação', x='Data', title='AVALIAÇÕES DIÁRIAS', labels={
    'Avaliação': 'Avaliação',
    'Dia': 'Dia'
})

# fig_date.add_shape(type="line", line_color="red", line_width=2, opacity=1, line_dash="solid", x0=0, x1=1, xref="paper", y0=mediana, y1=mediana, yref="y", name="Mediana")
# fig_date.add_shape(type="line", line_color="green", line_width=3, opacity=1, line_dash="solid", x0=0, x1=1, xref="paper", y0=media, y1=media, yref="y", name="Média")
# fig_date.add_shape(type="line", line_color="yellow", line_width=2, opacity=1, line_dash="solid", x0=0, x1=1, xref="paper", y0=moda, y1=moda, yref="y", name="Moda")
# fig_date.update_traces(textposition="bottom right")

# fig_date.update_xaxes(tickmode='linear', tick0=0, dtick=500)  # Ajusta o eixo x
# fig_date.update_yaxes(range=[valores_min - 1, valores_max + 1])  # Ajusta o eixo y para incluir o mínimo e máximo com uma pequena margem


# Criando as colunas na interface do Streamlit
col1_top, col2_top = st.columns(2)
col2_1top, col2_2top = col2_top.columns(2)
col1_bottom, col2_bottom, col3_bottom = st.columns(3)
col1_top.plotly_chart(fig_date, use_container_width=True)

# Gráfico de barras dos valores máximos e mínimos
fig_maxima = px.bar(df_max_min, x='Tipo', y='Valor', color="Tipo", title='VALORES MÁXIMOS E MÍNIMOS')
fig_maxima.update_layout(legend_title_text='Legenda')
col2_2top.plotly_chart(fig_maxima, use_container_width=True)

# Gráfico de pizza das médias
fig_medias = px.pie(names=['Média', 'Mediana', 'Moda'], values=[media, mediana, moda], title='MÉDIA, MEDIANA E MODA')
col2_1top.plotly_chart(fig_medias, use_container_width=True)

# Gráfico de barras das classes
fig_classes = px.bar(df_classes, x='Classe', y='Contagem', hover_data=['Limite Inferior', 'Limite Superior'], labels={
    'Contagem': 'Contagem de Valores',
    'Classe': 'Classe'
}, title='DISTRIBUIÇÃO DAS AVALIAÇÕES EM CLASSES', color_discrete_sequence=['blue'], template='plotly_white')
col1_bottom.plotly_chart(fig_classes, use_container_width=True)

# Tabela de frequências
col2_bottom.markdown("### FREQUÊNCIAS")
col2_bottom.write(df_frequencias, use_container_width=True)

# Tabela de limites e ponto médio
col3_bottom.markdown("### LIMITES E PONTO MÉDIO")
col3_bottom.write(df_limites_classes, use_container_width=True)

# st.dataframe(df)
# st.write(f"Média: {media}")
# st.write(f"Mediana: {mediana}")
# st.write(f"Moda: {moda}")