import streamlit as st
import pandas as pd
import numpy as np
import utils as ut
import matplotlib.pyplot as plt

st.set_page_config(page_title="Dashboard de Ventas - Farmacia San Jose", layout="wide")

st.title('Dashboard de Ventas - Farmacia San Jose')

# Cargar archivo
xlsx = st.file_uploader("Sube el archivo de ventas en formato xlsx")

if xlsx:
    df = ut.clean_and_get_xlsx(xlsx)

    st.header("Datos Originales")
    st.write(df)

    acumulado = ut.acumulado_por_horas(df)

    st.header("Datos Acumulados")
    st.write(acumulado)
    st.write(acumulado.columns.tolist())

    # Asegurarse de que 'Importe' sea numérico
    df['Importe'] = pd.to_numeric(df['Importe'], errors='coerce')
    
    # Extraer la hora como entero
    df['HoraEntera'] = pd.to_datetime(df['Hora'], format='%H:%M:%S').dt.hour

    # Diseño del dashboard en columnas
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Gráfica de Tendencia de Ventas por Hora")
        ventas_por_hora = df.groupby('HoraEntera').agg({'Importe': 'sum'}).reset_index()
        fig1, ax1 = plt.subplots(figsize=(10, 6))
        ax1.plot(ventas_por_hora['HoraEntera'], ventas_por_hora['Importe'], marker='o')
        ax1.set_title('Ventas por Hora del Día')
        ax1.set_xlabel('Hora del Día')
        ax1.set_ylabel('Importe Total de Ventas')
        ax1.grid(True)
        ax1.set_xticks(range(0, 24))
        st.pyplot(fig1)

        st.subheader("Gráfica Comparativa de Ventas Última Hora")
        ultima_hora = df[df['HoraEntera'] == 21]['Importe'].sum()
        penultima_hora = df[df['HoraEntera'] == 20]['Importe'].sum()
        comparativa_horas_df = pd.DataFrame({
            'Hora': ['20:00 - 21:00', '21:00 - 22:00'],
            'Importe': [penultima_hora, ultima_hora]
        })
        st.bar_chart(comparativa_horas_df.set_index('Hora')['Importe'])

    with col2:
        st.subheader("Gráfica de Ventas por Turno")
        turnos = {
            'Mañana': (6, 14),
            'Tarde': (14, 22),
            'Noche': (22, 6)
        }
        ventas_por_turno = []
        for turno, (inicio, fin) in turnos.items():
            if inicio < fin:
                ventas = df[(df['HoraEntera'] >= inicio) & (df['HoraEntera'] < fin)]['Importe'].sum()
            else:
                ventas = df[(df['HoraEntera'] >= inicio) | (df['HoraEntera'] < fin)]['Importe'].sum()
            ventas_por_turno.append((turno, ventas))
        ventas_por_turno_df = pd.DataFrame(ventas_por_turno, columns=['Turno', 'Importe'])
        st.bar_chart(ventas_por_turno_df.set_index('Turno')['Importe'])

        st.subheader("Gráfica de Ventas Acumuladas por Hora")
        df['ImporteAcumulado'] = df.groupby('HoraEntera')['Importe'].cumsum()
        ventas_acumuladas = df.groupby('HoraEntera').agg({'ImporteAcumulado': 'last'}).reset_index()
        fig2, ax2 = plt.subplots(figsize=(10, 6))
        ax2.plot(ventas_acumuladas['HoraEntera'], ventas_acumuladas['ImporteAcumulado'], marker='o')
        ax2.set_title('Ventas Acumuladas por Hora del Día')
        ax2.set_xlabel('Hora del Día')
        ax2.set_ylabel('Importe Acumulado de Ventas')
        ax2.grid(True)
        ax2.set_xticks(range(0, 24))
        st.pyplot(fig2)

    st.subheader("Gráfica de Dispersión para Acumulados")
    st.scatter_chart(data=acumulado, x="HoraRango", y="acumulado pesos")

    st.subheader("Gráfica de Análisis de Todas las Ventas del Mes por Hora")
    df['FechaHora'] = pd.to_datetime(df['Fecha'].astype(str) + ' ' + df['Hora'].astype(str))
    fig3, ax3 = plt.subplots(figsize=(15, 8))
    ax3.scatter(df['FechaHora'], df['Importe'], alpha=0.5)
    ax3.set_title('Análisis de Todas las Ventas del Mes por Hora')
    ax3.set_xlabel('Fecha y Hora')
    ax3.set_ylabel('Importe de Ventas')
    ax3.grid(True)
    st.pyplot(fig3)
