import streamlit as st
import pandas as pd
import re
import io

buffer = io.BytesIO()

st.title('Validador 0800')

arquivo = st.file_uploader("Escolha um arquivo", type=['xlsx', 'csv'])

if arquivo:
    df = pd.read_excel(arquivo)
    
    try:
        df['validador atendimento'] = df['atendimentoid'].apply(lambda x: x.isnumeric())
    except:
        df['atendimentoid'] = df['atendimentoid'].astype(str)
        df['validador atendimento'] = df['atendimentoid'].apply(lambda x: x.isnumeric())
        
    try:
        df['placa'] = df['placa'].apply(lambda x: x.upper())
    except:
        df['placa'] = df['placa'].astype(str)
        df['placa'] = df['placa'].apply(lambda x: x.upper())

    placas = df['placa']
    import re

    def verifica_placa_valida(serie):
        # Expressão regular para verificar o formato de placas brasileiras (antigas) e do Mercosul
        padrao_placa = r'^[A-Z]{3}\d{4}$|^[A-Z]{3}\d{1}[A-Z]{1}\d{2}$'

        # Função para verificar se a string é uma placa válida
        def eh_placa_valida(placa):
            return re.match(padrao_placa, placa) is not None

        # Aplica a função de verificação em cada elemento da série
        resultado = serie.apply(eh_placa_valida)

        return resultado


    # Criando um DataFrame de exemplo
    #df = pd.DataFrame({'Placas': ['RMY5H83', 'XYZ4567', 'SHS1I71', 'DEF8GHI']})

    # Chamando a função para verificar se as placas são válidas
    resultado = verifica_placa_valida(df['placa'])
    
    df['validador placa'] = resultado
    df['Validador geral Atendimento + PLaca'] = df['validador placa'] & df['validador atendimento']
    df['atendimento = placa'] = df['atendimentoid'] == df['placa']
    df.columns = ['Submission Date',
     'atendimentoid',
     'placa',
     'Nota',
     'validador atendimento',
     'validador placa',
     'Validador geral Atendimento + PLaca',
     'atendimento = placa']
    
    st.markdown('# Pronto!')
    
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        # Write each dataframe to a different worksheet.
        df.to_excel(writer, sheet_name='Sheet1')
    
    # Close the Pandas Excel writer and output the Excel file to the buffer
    writer.save()
    
    st.download_button(
        label="Download Excel",
        data=buffer,
        file_name="0800_validado.xlsx",
        mime="application/vnd.ms-excel"
    )