import datetime
import requests
import urllib
import os.path
import zipfile
from os import listdir
import csv
import os
import glob
import pandas as pd
from os import chdir
from glob import glob
import sys
import matplotlib.pyplot as plt

pastaCSV='csvs/'
pastaZip='zips/'
flrecriarArquivoCSV = False


def downloadFile(url, fileName):
    try:
        if not(os.path.exists(pastaZip)):
            os.mkdir(pastaZip)

        filezip = pastaZip+fileName+'.zip'

        if not(os.path.exists(filezip)):
            flUpdateCSV = True
            print('Fazendo download do arquivo ano/mes',fileName)
            urllib.request.urlretrieve(url, filezip)
            flrecriarArquivoCSV = True

    except:
        print('Erro baixando arquivo ',url,' talvez os dados não estejam disponíveis')

    ZIPtoCSV(filezip,fileName)

def ZIPtoCSV(filezip,filename):
    try:
        if not (os.path.exists(pastaCSV)):
            os.mkdir(pastaCSV)

        filecsv = filename+'_CPGF.csv'

        if not(os.path.exists(pastaCSV+filecsv)):
            fantasy_zip = zipfile.ZipFile(filezip)
            fantasy_zip.extract(filecsv,pastaCSV)
            fantasy_zip.close()
    except:
        print('')

def find_csv_filenames(path_to_dir, suffix=".csv" ):
    files = []
    fileDir = listdir(path_to_dir)
    for filename in fileDir:
        if filename.endswith(suffix):
            files.append(path_to_dir+filename)
    return files


def AgrupaCSV(list_of_files, file_out):
    try:
        combined_csv = pd.concat([pd.read_csv(f,sep=';', encoding='ANSI') for f in list_of_files])
        combined_csv.to_csv(file_out,sep=';',header=False)

    except:
       print("Unexpected error:", sys.exc_info()[0])
       print("Unexpected error:", sys.exc_info()[1])
       print("Unexpected error:", sys.exc_info()[2])

def main():
    FazerDownload=True
    anoCorrente = datetime.datetime.now().year
    mesCorrente = datetime.datetime.now().month
    portalTransparencia = 'http://www.portaldatransparencia.gov.br/download-de-dados/cpgf/'
    for ano in range(2013,anoCorrente+1):
       for mes in range(1, 12+1):
           if FazerDownload:
               if mes<=9: #:Adiciona a string 0 nos meses de 1 a 9
                  mescomzero = '0'+str(mes)
               else:
                  mescomzero = str(mes)

               fileName = str(ano)+mescomzero

               #Download e unzip
               downloadFile(portalTransparencia+fileName,fileName)

               if ano == anoCorrente and mes == mesCorrente:
                  FazerDownload = False

    listcsvFiles = find_csv_filenames(pastaCSV)

    file_out = 'DadosReunidos.csv'
    if flrecriarArquivoCSV:
        AgrupaCSV(listcsvFiles, file_out)
    cols = [  'CÓDIGO ÓRGÃO SUPERIOR',
              'NOME ÓRGÃO SUPERIOR',
              'CÓDIGO ÓRGÃO',
              'NOME ÓRGÃO',
              'CÓDIGO UNIDADE GESTORA',
              'NOME UNIDADE GESTORA',
              'ANO EXTRATO',
              'MÊS EXTRATO',
              'CPF PORTADOR',
              'NOME PORTADOR',
              'CNPJ OU CPF FAVORECIDO',
              'NOME FAVORECIDO',
              'TRANSAÇÃO',
              'DATA TRANSAÇÃO',
              'VALOR TRANSAÇÃO']


    df =   pd.read_csv(file_out,sep=";",names=cols, header=None)
    df['VALOR TRANSAÇÃO'] = df['VALOR TRANSAÇÃO'].str.replace(',', '.').astype(float)
    df["ANO EXTRATO"] = df["ANO EXTRATO"].astype(str)

    ####Gastos gerais do Governo##################
    df = df[(df['NOME ÓRGÃO SUPERIOR'] == 'Presidência da República')]
    df = df.groupby(['ANO EXTRATO', 'MÊS EXTRATO'])["VALOR TRANSAÇÃO"].sum()
    print(df)

    ax = df.plot(x=['ANO EXTRATO', 'MÊS EXTRATO'], y="VALOR TRANSAÇÃO", kind='bar', fontsize=7, color="indigo");
    ax.set_title("Gastos do governo desde 2013 - Apenas Presidência da República", fontsize=15)
    ax.set_ylabel("Milhões", fontsize=15);
    ax.set_xlabel("Ano", fontsize=15);
    mng = plt.get_current_fig_manager()
    mng.window.state('zoomed')  # works fine on Windows!
    plt.show()
    ################################################################

main()


