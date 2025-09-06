
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

lambd = 1
k = 10    #n de ativos a ser selecionado

n_stocks = len(codes)
return_total = []
risk_total = []
data = {'Retorno': return_total, 'Risco': risk_total}

i = 0
while i<n_stocks:
  data[str(codes[i])] = []
  i += 1

data['List'] = []

indexes = []
selected_risk = []
testdict = {'indexes':indexes, 'selected':selected_risk}

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


def simanneal_firstcycle(n_stocks, codes, gain, volatility, risks):

  global lambd
  global data
  global k

  #número de portfolios a ser calculado; definido arbitrariamente
  iterations = 1000

  #define um dicionário contendo todos os dados
  

               
  max = n_stocks

  best_risk = 10000
  best_index = 0
  true_lowest = 10000
  custom_index = 0

  for i in range(0,iterations):
    #vetor para conter os pesos gerados
    weights = []

    ###BINARY STRING GENERATION

    def binary_string_gen(max, k):

      arr = [0]*max

      i = 0
      sum = 0
      iter = 1

      sortear = randint(0,1)
      if sortear == 1:
          i = max-1
          iter = -1

      #print(f"sortear: {sortear}")

      while sum < k:

          if arr[i] == 0:
              arr[i] = randint(0,1)
              sum += arr[i]

          if (iter == -1 and i-1 == -1) or (i+1 == max and iter == 1):
              iter *= -1

          i += iter

      return arr

    def random_weight_gen(k, arr):
      y = 0
      
      i=0
      counter = 0
      while counter < k:
        if arr[i] == 1:
          arr[i] = uniform(0,20)
          y += arr[i]
          counter +=1
        i += 1

      i=0
      counter = 0
      while counter < k:
        if arr[i] != 0:
          arr[i] = arr[i]/y
          counter +=1
        i += 1

      return arr
    
    weights = binary_string_gen(max, k)
    weights = random_weight_gen(k, weights.copy())
    
    for x in range(0,n_stocks):
      data[str(codes[x])].append(weights[x])

    data['List'].append(weights)

    ###BINARY STRING GENERATION - END

    sum, current_risk = markowitz(weights, gain, volatility, risks)
    
    data['Retorno'].append(sum)
    data['Risco'].append(current_risk)

    if current_risk < best_risk:
      best_risk = current_risk
      best_index = data['Risco'].index(current_risk)

    if current_risk < true_lowest:
      true_lowest = current_risk

    testdict['indexes'].append(custom_index)
    testdict['selected'].append(best_risk)
    custom_index += 1


  #Insere o dicionario local contendo riscos, ganhos e pesos 
  #no dicionario da memoria compartilhada

  #portfolios = pd.DataFrame(data)
  #print(data)
  return best_index, true_lowest, custom_index

def markowitz(weights, gain, volatility, risks):

  #soma todos os termos que consistem de variança*peso^2
  #aproveita e já normaliza os pesos
  i = 0
  sum_a = 0
  while(i<n_stocks):
    sum_a += weights[i]*weights[i]*volatility[i]*volatility[i]
    i += 1
  
  #soma todos os termos que consistem de 2*produtorio(peso)*covar
  i = 0
  sum_b = 0
  while(i<n_stocks):
    #o iterador j é feito dessa forma a fim de retirar somente as covarianças da matriz de risco, sem percorrer o mesmo valor novamente
    j=i+1
    while(j<n_stocks):
      sum_b += 2*weights[i]*weights[j]*risks[i][j]
      j += 1
    i += 1

  #risk_total.append(sum_a + sum_b) - WAIT FOR RETURNS INCLUSION

  i = 0
  sum = 0
  while(i<n_stocks):
    sum += gain[i]*weights[i]
    i += 1

  return_penalty = sum*(1-lambd)
  current_risk = sum_a + sum_b - return_penalty

  return sum, current_risk
  

def simanneal(gain, volatility, risks, alpha):
    E = 51              #number os steps or λ values
    N = 2               #number of assets
    risk_c = 0          #current calculated risk 
    risk_nb = 0         #a 'neighbour' calculated risk
    risk_min = 0        #the smallest risk found 
    #alpha = 0.70       #cooling factor
    
    global n_stocks
    global data_inicial
    global data_final
    global codes

    d_neighbours = 5
    c_neighbours = 100
    
    best_index, true_lowest, custom_index = simanneal_firstcycle(n_stocks, codes, gain, volatility, risks)
    T = data['Risco'][best_index]/10
    
    for e in range(0,E):
      contador = 0
      rejeita = 0
      #simanneal_firstcycle(n_stocks, codes, gain, volatility, risks)
      #T = data['Risco'][best_index]/10
      #print(f"no ciclo {e} a temperatura é: {T}")
      
      for i in range(0,d_neighbours):

        D = data['List'][best_index].copy()

        aux = 0
        
        while True:
          x = randint(0,n_stocks-1)
          if D[x] != 0:
            aux = D[x]
            D[x] = 0
            break
        
        while True:
          x = randint(0,n_stocks-1)
          if D[x] == 0:
            D[x] = aux
            break

        for j in range(0,c_neighbours):

          C = D.copy()
          
          h = 0 #real index of the vector
          y = 0 #sum for normalization
          counter = 0 
          while counter < k:
            if C[h] != 0:
              C[h] = C[h]*(uniform(-0.25, 0.25)+1)
              y += C[h]
              counter += 1
            h += 1

          h=0 #real index of the vector
          counter = 0 
          while counter < k:
              if C[h] != 0:
                C[h] = C[h]/y
                counter += 1
              h +=1

          sum, current_risk = markowitz(C, gain, volatility, risks)

          #implement selection and metropolis criterion

          #it's not likely that we'll get the exact same risk, except for the scenario where we generate
          #the exact same portfolio. So, in order to avoid duplicates created at least by this part of the
          #code, we test it for:
          if current_risk < data['Risco'][best_index]:

            for x in range(0,n_stocks):
              data[str(codes[x])].append(C[x])

            data['Retorno'].append(sum)
            data['Risco'].append(current_risk)
            data['List'].append(C)

            best_index = len(data['Risco']) - 1

          elif current_risk > data['Risco'][best_index]:

            for x in range(0,n_stocks):
              data[str(codes[x])].append(C[x])

            data['Retorno'].append(sum)
            data['Risco'].append(current_risk)
            data['List'].append(C)

            delta = current_risk - data['Risco'][best_index]
            u = uniform(0,1)
            metropolis = math.pow(2.57, (-1*delta)/T)

            if u < metropolis:
              contador += 1
              best_index = len(data['Risco']) - 1

          testdict['indexes'].append(custom_index)
          testdict['selected'].append(data['Risco'][best_index])
          custom_index += 1

          if current_risk < true_lowest:
            true_lowest = current_risk


      T = T*alpha
      #print(f"foram {contador} trocas")
      #print(f"foram {rejeita} reiejições")
      #print("")

    return best_index, true_lowest

def plot_markowitz(data, testdict, x):
  plt.rcParams["figure.figsize"] = [18.50, 16.50]
  
  portfolios = pd.DataFrame(data) 
  portfolios.plot.scatter(x='Risco', y='Retorno', c='green', marker='o', s=10, alpha=0.15)

  plt.savefig('d_c_images/portfolios'+ str(x) +'.png')

  #portfolios.savefig('portfolios1.png')



  testframe = pd.DataFrame(testdict) 
  #testframe.plot.scatter(x='indexes', y='selected', c='green', marker='o', s=10, alpha=1)
  testframe.plot('indexes', 'selected')

  lenindx = len(testdict['selected'])

  best_risk = testdict['selected'][lenindx-1]

  #keep in mind that you're specifying vectors, so it should look like a vector sum
  xa = [0, lenindx - 1]
  ya = [best_risk, best_risk]
  plt.plot(xa, ya, marker = 'o')

  plt.savefig('d_c_images/selection'+ str(x) +'.png')

  plt.close('all')

  
  #plt.show()

def interface():

    overview = { 'risco': [], 'retorno': [], 'offset':[], 'exec':[]}

    result = setup(n_stocks, data_inicial, data_final, codes)
    gain = result[0]
    volatility = result[1]
    risks = result[2]

    testing_set = [(0,10,0.8),(10,20,0.75),(20,30,0.7)]
    #testing_set = [(0,2,0.8),(2,4,0.75),(4,6,0.7)]

    for start, stop, alpha in testing_set:

        for x in range(start, stop):
            start = time.time()
            best_index, true_lowest = simanneal(gain, volatility, risks, alpha)
            end = time.time()
            exec = end-start
            plot_markowitz(data, testdict, x)

            selected_risk = data['Risco'][best_index]
            selected_return = data['Retorno'][best_index]

            overview['risco'].append(selected_risk)
            overview['retorno'].append(selected_return)
            overview['offset'].append(selected_risk - true_lowest)
            overview['exec'].append(exec)

            for key, arr in data.items():
                arr.clear()

            for key, arr in testdict.items():
                arr.clear()

    overview = pd.DataFrame(overview)
    pd.set_option("display.max_rows", None, "display.max_columns", None)
    print(overview)
    overview.to_csv('d_c_results.csv')

interface()




