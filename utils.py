import pandas as pd

def clean_and_get_xlsx(file):
    # Leer el archivo Excel
    df = pd.read_excel(file, index_col=0)

    # Establecer la segunda fila (índice 1) como los nombres de las columnas
    df.columns = df.iloc[2]

    # Eliminar la segunda fila (índice 1) del DataFrame
    df = df[3:]

    # Resetear el índice del DataFrame
    df.reset_index(drop=True, inplace=True)

    # Filtrar el DataFrame para conservar solo las filas donde "cliente" es "CONTADO"
    df_filtered = df[df['Cliente'] == 'C O N T A D O ']

    # Eliminar la columna "Status"
    df_filtered.drop(columns=['Status'], inplace=True)

    return df_filtered

def acumulado_por_horas(df):
    # Convertir la columna 'Fecha' a datetime
    df['Fecha'] = pd.to_datetime(df['Fecha'])
    
    # Crear una columna de 'FechaHora' combinando 'Fecha' y 'Hora'
    df['FechaHora'] = pd.to_datetime(df['Fecha'].astype(str) + ' ' + df['Hora'].astype(str))
    
    # Crear una columna de rango de horas
    df['HoraRango'] = df['FechaHora'].dt.floor('2H')
    
    # Crear un nuevo dataframe para acumulado
    acumulado_df = df.groupby(['Fecha', 'HoraRango', 'Divisa']).agg({'Importe': 'sum'}).reset_index()
    
    # Pivotar la tabla para tener columnas separadas para pesos y dólares
    pivot_df = acumulado_df.pivot_table(index=['Fecha', 'HoraRango'], columns='Divisa', values='Importe', fill_value=0).reset_index()
    
    # Asegurarse de que las columnas 'Pesos' y 'Dlls' existan
    if 'Pesos' not in pivot_df.columns:
        pivot_df['Pesos'] = 0
    if 'Dlls' not in pivot_df.columns:
        pivot_df['Dlls'] = 0
        
    # Renombrar las columnas
    pivot_df.columns.name = None  # Elimina el nombre de la columna
    pivot_df = pivot_df.rename(columns={'Pesos': 'acumulado pesos', 'Dlls': 'acumulado dolares'})
    
    # Extraer el tipo de cambio (tc) por rango de hora
    df['tc'] = df['T.C.']
    tc_df = df.groupby(['Fecha', 'HoraRango']).agg({'tc': 'last'}).reset_index()
    
    # Unir el pivot_df con tc_df para agregar la columna de tipo de cambio
    result_df = pd.merge(pivot_df, tc_df, on=['Fecha', 'HoraRango'], how='left')
    
    # Extraer solo la hora para la columna de rango de horas
    result_df['HoraRango'] = result_df['HoraRango'].dt.strftime('%H:%M') + ' - ' + (result_df['HoraRango'] + pd.Timedelta(hours=2)).dt.strftime('%H:%M')
    
    # Asegurarse de cubrir todos los rangos de horas desde 6:00 - 8:00 hasta 22:00 - 00:00
    horas = pd.date_range("06:00", "22:00", freq="2H").time
    horas_rango = [pd.Timestamp(hora.strftime('%H:%M')).strftime('%H:%M') + ' - ' + (pd.Timestamp(hora.strftime('%H:%M')) + pd.Timedelta(hours=2)).strftime('%H:%M') for hora in horas]
    
    fechas = result_df['Fecha'].unique()
    all_combinations = pd.MultiIndex.from_product([fechas, horas_rango], names=["Fecha", "HoraRango"])
    result_df = result_df.set_index(["Fecha", "HoraRango"]).reindex(all_combinations, fill_value=0).reset_index()
    
    return result_df


def calcular_ventas_acumuladas(df):
    # Convertir la columna 'Fecha' a formato datetime
    df['Fecha'] = pd.to_datetime(df['Fecha'])
    
    # Extraer el día de la semana y agregarlo como una nueva columna
    df['Day_of_Week'] = df['Fecha'].dt.day_name()
    
    # Definir el orden de los días de la semana
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    # Agrupar por día de la semana y sumar la columna 'Importe' para encontrar el día con mayores ventas
    sales_summary = df.groupby('Day_of_Week')['Importe'].sum().reset_index()
    
    # Ordenar por el orden definido de los días de la semana
    sales_summary['Day_of_Week'] = pd.Categorical(sales_summary['Day_of_Week'], categories=days_order, ordered=True)
    sales_summary = sales_summary.sort_values('Day_of_Week')
    
    return sales_summary

