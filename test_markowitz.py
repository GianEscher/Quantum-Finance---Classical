
import pandas as pd
import yfinance as yfin
import numpy as np
import matplotlib.pyplot as plt
from pandas_datareader import data as pdr
from random import randint
from random import uniform
import math

import time

yfin.pdr_override()

data_inicial = "2020-09-01"
data_final = "2020-12-11"
codes = ["AKBNK.IS",
        "ASELS.IS",
        "EKGYO.IS",
        "EREGL.IS",
        "KRDMD.IS",
        "KCHOL.IS",
        "KOZAA.IS",
        "OYAYO.IS",
        "PETKM.IS",
        "AKFGY.IS",
        "TUPRS.IS",
        "TTKOM.IS",
        "HALKB.IS",
        "ARCLK.IS",
        "BIMAS.IS",
        "DOHOL.IS",
        "SAHOL.IS",
        "KOZAL.IS",
        "MGROS.IS",
        "PGSUS.IS",
        "TAVHL.IS",
        "ISCTR.IS",
        "SISE.IS",
        "FROTO.IS",   #Astor Enerji A.S. - manufacturer of transformer and switchgear (comutador) products
        "ENKAI.IS"]   #Enka Insaat ve Sanayi A.S. - engineering and construction Istanbul company
        #removed "TKGBY"
        #removed "TKC"
        #removed "TKHVY"

        #Fertilizer Mills Inc. - couldn't find about
        #Turkiye Industrial Development Bank Inc. - couldn't find a code

codes = ['goog',
        'msft',
        'ibm',
        'aapl']

data_inicial = "2017-01-01"
data_final = "2018-01-01"

#coef de aceitação de risco, converte retorno em risco
#range: 1-0, 1 retorna menor risco, 0 retorna melhor combinação retorno máx e risco
lambd = 1 


n_stocks = len(codes)
return_total = []
risk_total = []
data = {'Retorno': return_total, 'Risco': risk_total}

i = 0
while i<n_stocks:
  data[str(codes[i])] = []
  i += 1

data['List'] = []

def setup(n_stocks, data_inicial, data_final, codes):

  #essas são as duas datas mencionadas no princípio deste documento.
  #data_inicial = input('insert the start data, as "yyyy-mm-dd": ')
  #data_final = input('insert the ending data, as "yyyy-mm-dd": ')

  #para cada ação, o laço repetirá, processando resultando sempre em uma média, um desvio padrão e um vetor de erros percentuais consecutivos
  #estes, por sua vez, serão adicionados em ordem nos vetores globais correspondentes 
  
  gain = []
  volatility = []
  stocks_registry = []

  i=0
  while(i<n_stocks):

    #o primeiro dos vetores abaixo recebe os dados de fechamento brutos da ação.
    #o vetor stocks-_gain[], por sua vez, armazena temporariamente os erros percentuais consecutivos calculados, para então
    #adicioná-los à matriz stocks_registry[] e ainda facilitr os cálculos de média e desvio padrão
    
    stocks_raw = []
    stocks_gain = []

    #Observation: apparently, if i append a global list inside another global list, any alterations made to the former will be DINAMICALLY
    #updated in the latter too search for that later. seems like quite the phantasmagorical behaviour

    #stocks = input('insert the stock code: ')
    stocks = codes[i]
    history = pdr.DataReader(stocks, data_inicial, data_final)#recupera os dados do banco de dados do Yahoo Finance

    stocks_raw = history['Close'].tolist()#retira somente a coluna de dados de fechamento do dataframe recebido
    
    #o laço while abaixo calcula os erros percentuais consecutivos
    j=1
    while(j<len(stocks_raw)):
      stocks_gain.append(((stocks_raw[j]-stocks_raw[j-1])/stocks_raw[j-1]))
      j+=1
    stocks_registry.append(stocks_gain)#adiciona os erros percentuais, em porcentagem, à matriz global

    #a média é calculada em seguida
    sum = 0
    for a in stocks_gain:
      sum += a
    mean = sum/len(stocks_gain)
    
    mean_monthly = 0
    if mean>0:
      mean_monthly = np.power(mean+1,21)-1
    elif mean < 0:
      mean_monthly = np.power(mean-1,21)+1#o exp eh impar, portanto n ha problema no sinal da potencia - permanece negativo
    gain.append(mean_monthly)

    
    #cálculo do desvio padrão. Preferiu-se fazê-lo a fim de reduzir o número de raízes calculadas, uma vez que
    #computacionalmente falando, cálculo de potências é mais performático
    sd = 0
    j=0
    while(j<len(stocks_gain)):
      sd += ((mean-stocks_gain[j])*(mean-stocks_gain[j]))
      j += 1
    sd = np.sqrt(sd*21/len(stocks_gain))  
    volatility.append(sd)

    i+=1
  
  
  #construção da matriz de risco

  risks = []
  i=0
  while(i<len(volatility)):
    j=0
    row = []

    while(j<len(volatility)):
      if(i==j):
        variat = volatility[i]*volatility[i]
        row.append(variat)
        
      else:
        covariat = covar(stocks_registry[i],gain[i],stocks_registry[j],gain[j])
        row.append(covariat)
      
      j+=1

    risks.append(row)
    i+=1

  return [gain, volatility, risks]

  #return markowitz(n_stocks, codes, gain, volatility, risks)
  
  #start = time.time()
  #call =  markowitz(n_stocks, codes, gain, volatility, risks)
  #end = time.time()
  #print("Markowitz def average consumed time")
  #print(end-start)
    
#função responsável por calcular a covariânça, dado os erros percentuais consecutivos e a média de duas ações
def covar(list_A, mean_A, list_B, mean_B):
  sum = 0
  i=0
  lenght=len(list_A)
  lenght2 = len(list_B)



  while(i<lenght):
    sum+=(list_A[i]-mean_A)*(list_B[i]-mean_B)
    i+=1
    
  return sum/lenght  


def portfolio_gen(gain, volatility, risks, best_index):

  global lambd
  global data

  #número de portfolios a ser calculado; definido arbitrariamente
  iterations = 3773
     
  max = n_stocks

  best_risk = 10000


  for i in range(0,iterations):
    #vetor para conter os pesos gerados
    weights = []

    ###RANDOM STRING GENERATION

    def random_string_gen(max):

      y = 0
      arr = [0]*max
      
      i=0
      while i<max:
        arr[i] = uniform(0,20)
        y += arr[i]
        i += 1

      i=0
      while i<max:
          arr[i] = arr[i]/y
          i +=1

      return arr

    weights = random_string_gen(max)
    
    for x in range(0,n_stocks):
      data[str(codes[x])].append(weights[x])

    data['List'].append(weights)

    ###RANDOM STRING GENERATION - END

    sum, current_risk = markowitz(weights, gain, volatility, risks)
    
    data['Retorno'].append(sum)
    data['Risco'].append(current_risk)

    if current_risk < best_risk:
      best_risk = current_risk
      best_index = data['Risco'].index(current_risk)


  return best_index

def markowitz(weights, gain, volatility, risks):

  #soma todos os termos que consistem de variança*peso^2
  i = 0
  sum_a = 0
  while(i<n_stocks):
    sum_a += weights[i]*weights[i]*volatility[i]*volatility[i]
    i += 1
  
  #soma todos os termos que consistem de 2*peso i*peso j*covar
  i = 0
  sum_b = 0
  while(i<n_stocks):
    #o iterador j é feito dessa forma a fim de retirar somente as covarianças da matriz de risco, sem percorrer o mesmo valor novamente
    j=i+1
    while(j<n_stocks):
      sum_b += 2*weights[i]*weights[j]*risks[i][j]
      j += 1
    i += 1

  i = 0
  sum = 0
  while(i<n_stocks):
    sum += gain[i]*weights[i]
    i += 1

  return_penalty = sum*(1-lambd)
  current_risk = sum_a + sum_b - return_penalty

  return sum, current_risk
  

def plot_markowitz(data, x):
  plt.rcParams["figure.figsize"] = [18.50, 16.50]
  
  portfolios = pd.DataFrame(data) 
  portfolios.plot.scatter(x='Risco', y='Retorno', c='green', marker='o', s=10, alpha=0.15)

  plt.savefig('teste2/portfolios'+ str(x) +'.png')

  #portfolios.savefig('portfolios1.png')



  #testframe = pd.DataFrame(testdict) 
  #testframe.plot.scatter(x='indexes', y='selected', c='green', marker='o', s=10, alpha=1)
  #testframe.plot('indexes', 'selected')

  #lenindx = len(testdict['selected'])

  #best_risk = testdict['selected'][lenindx-1]

  #keep in mind that you're specifying vectors, so it should look like a vector sum
  #xa = [0, lenindx - 1]
  #ya = [best_risk, best_risk]
  #plt.plot(xa, ya, marker = 'o')

  #plt.savefig('c_images/selection'+ str(x) +'.png')

  plt.close('all')

  
  #plt.show()

def interface():

    overview = { 'risco': [], 'retorno': [], 'exec':[]}

    result = setup(n_stocks, data_inicial, data_final, codes)
    gain = result[0]
    volatility = result[1]
    risks = result[2]

    for x in range(0,1):
        start = time.time()
        #best_index, true_lowest = simanneal(gain, volatility, risks)
        best_index = 0
        for y in range(0,53):
            best_index = portfolio_gen(gain, volatility, risks, best_index)
        end = time.time()
        exec = end-start
        plot_markowitz(data, x)

        selected_risk = data['Risco'][best_index]
        selected_return = data['Retorno'][best_index]
        for h in codes:
          print(f'{h}: {data[h][best_index]}')

        overview['risco'].append(selected_risk)
        overview['retorno'].append(selected_return)
        #overview['offset'].append(selected_risk - true_lowest)
        overview['exec'].append(exec)

        for key, arr in data.items():
            arr.clear()

        #for key, arr in testdict.items():
        #    arr.clear()

    overview = pd.DataFrame(overview)
    pd.set_option("display.max_rows", None, "display.max_columns", None)
    print(overview)
    overview.to_csv('mark_results.csv')

interface()




