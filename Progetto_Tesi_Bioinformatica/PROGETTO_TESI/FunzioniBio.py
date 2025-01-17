import concurrent.futures
import json
import numpy as np
import multiprocessing
import time
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import re

from scipy.stats import entropy
from scipy import integrate
from Istogrammatore import Istogrammatore
from DatiFinestra import DatiFinestra
from pathlib import Path
import csv

NUMERO_CORE = multiprocessing.cpu_count()
LIMITE_SINGLE_CORE = 10000
NUM_BP_FINESTRA = 1000
NUM_SEQUENZE = 5
NUM_BASI_MER = 12
PERCENTUALE = 0.1
DIVISORE_GRAFICO_RIPETIZIONI = 1000
MAX_LIMITE_X = 10000

'''
caricaCromosoma carica il cromosoma e lo prepara per l'elaborazione
'''
def caricaCromosoma(cromosoma, estensione):
    f = open('Genoma_Umano/'+cromosoma+estensione)
    app = f.readline()
    cromosoma = f.read() #cromosoma senza la prima riga
    cromosoma = re.sub("\n","",cromosoma)
    return cromosoma

'''
---------------------------------------------------------------------
suddivisioneCromosomaFinestre effettua una suddivisione del cromosoma
in finestre composte ciascuna da 1000 basi azotate    
---------------------------------------------------------------------
'''
def suddivisioneCromosomaInFinestre(cromosoma):
    finestra = []
    i = 0
    j = NUM_BP_FINESTRA
    while j <= len(cromosoma):
        finestra.append(cromosoma[i:j])
        if j == len(cromosoma):
            break
        i = i + NUM_BP_FINESTRA
        if i < (len(cromosoma) - NUM_BP_FINESTRA):
            j = j + NUM_BP_FINESTRA
        else:
            j = len(cromosoma)
    finestra = np.array(finestra)
    return finestra

'''
---------------------------------------------------------------------
suddivisioneFinestreInMers effettua una suddivisione delle finestre
di ciascun cromosoma in 12-mers composti da 12 basi azotate  
---------------------------------------------------------------------
'''
def suddivisioneFinestreInMers(finestra):
    finestre_mers = []
    for cont in range(0, len(finestra)):
        print(cont," SU: ",len(finestra), "1")
        lunghezzaFinestraCorrente = len(finestra[cont]) - NUM_BASI_MER
        mers = []
        for i in range(0, lunghezzaFinestraCorrente + 1):
            if i < lunghezzaFinestraCorrente:
                mers.append(finestra[cont][i : i + NUM_BASI_MER])
            else:
                mers.append(finestra[cont][i : len(finestra[cont])])
        finestre_mers.append(mers)
    return finestre_mers
'''
---------------------------------------------------------------------
calcoloMatch calcola i vari match per ogni kmer di ciascuna finestra 
confrontandoli con il resto della finestra
---------------------------------------------------------------------
'''
def calcoloMatch(finestre_mers):
    matches_finestra = []
    for cont in range(0, len(finestre_mers)):
        print(cont," SU: ",len(finestre_mers))
        diz = {}
        cont_matches = 0
        for i in range(0, len(finestre_mers[cont])):
            kmer = str(finestre_mers[cont][i])
            if kmer not in diz.keys():
                diz[kmer] = 0
            diz[kmer] = diz[kmer] + 1
        for val in diz.values():
            if val > 1:
                cont_matches += val - 1
        matches_finestra.append(cont_matches)
    return matches_finestra
'''
----------------------------------------------------------------------
ricalcoloFinestre effettua un ricalcolo delle finestre di ciascun 
cromosoma andando a tenere in considerazione quelle che possiedono
un numero di matches superiore al 10% rispetto al numero di mer totali
----------------------------------------------------------------------
'''
def ricalcoloFinestre(cartellaRisultati, nomefile, cromosoma, finestre_mers, matches_finestra):
    fl = open(cartellaRisultati+"Test/Risultati_finestre_pre_raggruppamento_"+nomefile+".txt", "w")
    fl.write('numero_finestra, ' + 'posizione_iniziale, ' + 'ripetizioni' + '\n')

    visualizzatore_cromosoma = []
    conta_finestre = []
    pos = []

    cont = 0
    k = 0

    for _ in range(int(len(finestre_mers)//DIVISORE_GRAFICO_RIPETIZIONI) + 1):
        visualizzatore_cromosoma.append(0)
        conta_finestre.append(0)
    while cont < len(finestre_mers):
        dieci_percento = len(finestre_mers[cont]) * PERCENTUALE
        posizione = int(cont//DIVISORE_GRAFICO_RIPETIZIONI)
        if matches_finestra[cont] > dieci_percento:
            fl.write(str(cont+1) + ', ' + str(k) + ', SI\n')
            visualizzatore_cromosoma[posizione] += 1
            print(posizione,", ",len(finestre_mers))
            conta_finestre[posizione] = posizione
            k = k + NUM_BP_FINESTRA
            pos.append(cont)
        else:
            fl.write(str(cont+1) + ', ' + str(k) + ', NO\n')
            conta_finestre[posizione] = posizione
            k = k + NUM_BP_FINESTRA
        if k >= len(cromosoma):
            break
        cont = cont + 1
    fl.close()
    with open(cartellaRisultati+"SavedFiles/visualizzatore_"+nomefile+".json", "w") as fl:
        json.dump(visualizzatore_cromosoma, fl)
    return pos
'''
----------------------------------------------------------------------
creazioneNuoveFinestre crea una lista in cui vengono inserite tutte le 
finestre con un numero di ripetizioni maggiore del 10%
----------------------------------------------------------------------
'''
def creazioneNuoveFinestre(cartellaRisultati, nomefile, finestra, pos):
    nuove_finestre = []
    entrato = False
    ft = open(cartellaRisultati+"Test/Risultati_finestre_raggruppamento_"+nomefile+".txt", "w")
    ft.write('numero_finestra, ' + 'posizione_iniziale, ' + 'numero_basi\n')

    with open(cartellaRisultati+"SavedFiles/visualizzatore_"+nomefile+".json", "r") as fl:
        visualizzatore_cromosoma = json.load(fl)

    i = 1
    cont = 0
    pos_precedente = pos[0]
    n_finestra = finestra[pos[0]]
    indice = 1
    p_i = 0
    lista_posizioni=[]
    while cont < len(finestra):
        print(cont," SU: ",len(finestra))
        if i < len(pos):
            if cont == pos[i]:
                if pos[i] == (pos_precedente + 1):
                    n_finestra = n_finestra + finestra[cont]
                    entrato = True
                else:
                    nuove_finestre.append(n_finestra)
                    ft.write(str(indice) + ', ' + str(p_i) + ', ' + str(len(n_finestra)) + '\n')
                    lista_posizioni.append(p_i)
                    p_i = pos[i] * NUM_BP_FINESTRA
                    indice = indice + 1
                    if entrato:
                        entrato = False
                        n_finestra = finestra[cont]
                    else:
                        n_finestra = finestra[cont]
                pos_precedente = pos[i]
                i = i + 1
            cont = cont + 1
        else:
            break
    nuove_finestre.append(n_finestra)
    lista_posizioni.append(p_i)
    ft.write(str(indice) + ', ' + str(p_i) + ', ' + str(len(n_finestra)) + '\n')
    ft.close()
    with open(cartellaRisultati+"SavedFiles/Posizioni_finestre"+nomefile+".json", "w") as fl:
        json.dump(lista_posizioni, fl)
    with open(cartellaRisultati+"SavedFiles/nuove_finestre_"+nomefile+".json", "w") as fl:
        json.dump(nuove_finestre, fl)
'''
--------------------------------------------------------------------------
calcoloDistanzeMatch effettua un calcolo delle distanze di tutti i matches
trovati all'interno di ciascuna finestra ricalcolata, salvandone anche il
valore del numero di occorrenze
--------------------------------------------------------------------------
'''
def calcoloDistanzeMatch(cartellaRisultati, nomefile):
    with open(cartellaRisultati+"SavedFiles/Posizioni_finestre"+nomefile+".json", "r") as fl:
        dimFinestre = json.load(fl)
    with open(cartellaRisultati+"SavedFiles/nuove_finestre_"+nomefile+".json", "r") as fl:
        nuove_finestre = json.load(fl)

    datiVisualizzazione = open(cartellaRisultati+"/dati_finestre_"+nomefile+".csv", "w")
    writer = csv.writer(datiVisualizzazione)
    writer.writerow(["Posizione iniziale", "Posizione finale", "Dimensione", "Entropia Shannon", "Indice di Simpson", "Numero ripetizioni"])
    executor = concurrent.futures.ProcessPoolExecutor()
    matches = []

    #with open(cartellaRisultati+"/nuove_finestre_"+nomefile, "r") as fl:
    #    nuove_finestre = json.load(fl)

    #distTemp = open(cartellaRisultati+"/distanze_temp_"+nomefile+".txt", "w")

    distDistanze = []
    for cont in range(0, len(nuove_finestre)):
        buffers = {}
        cont_matches = 0
        diz_dis_freq = {}
        diz = {}
        stringaStampa = ""
        for i in range(0, len(nuove_finestre[cont]) - NUM_BASI_MER):
            stringaStampa = "I: ", i, "SU: ", (len(nuove_finestre[cont]) - NUM_BASI_MER), "CONT: ", cont, "SU: ", len(nuove_finestre)
            print(stringaStampa)
            kmer = str(nuove_finestre[cont][i: i + NUM_BASI_MER])
            if kmer not in diz.keys():
                diz[kmer] = []
            else:
                cont_matches += 1
            diz[kmer].append(i + NUM_BASI_MER)

        percentuale = 0
        ripetizioniFatte = 0
        for listaRipetizioni in diz.values():
            ripetizioniFatte += len(listaRipetizioni)
            percentuale = ripetizioniFatte/((len(nuove_finestre[cont]) - NUM_BASI_MER)/100)
            print(stringaStampa," ", percentuale,"%")
            if len(listaRipetizioni) > 2000 and len(listaRipetizioni) < 100000:
                posizione = 2000 * (len(listaRipetizioni)//2000)
                print("STO USANDO IL BUFFER ",posizione,"?")
                if posizione not in buffers.keys():
                    buffers[posizione] = []
                listaRipetizioni = np.array(listaRipetizioni)
                buffers[posizione].append(listaRipetizioni)
                gestisci_buffer(buffers[posizione], executor, diz_dis_freq)

            elif len(listaRipetizioni) > 100000:
                buffer = []
                for k in range(NUMERO_CORE):
                    nuovaLista = []
                    buffer.append(nuovaLista)
                for i in range(0, len(listaRipetizioni) - 1, NUMERO_CORE):
                    if i + NUMERO_CORE > len(listaRipetizioni) - 1:
                        for j in range(len(listaRipetizioni) - 1 - i):
                            buffer[j].append(i + j)
                        break
                    for k in range(NUMERO_CORE):
                        buffer[k].append(i + k)
                print("STO ESEGUENDO SU: ", len(listaRipetizioni))
                listaRipetizioni = np.array(listaRipetizioni)
                for i in range(len(buffer)):
                    print(len(buffer[i]))
                    buffer[i] = np.array(buffer[i])
                results = [executor.submit(calcola_match_singolo, listaRipetizioni, k) for k in buffer]
                for f in concurrent.futures.as_completed(results):
                    for dist in f.result().keys():
                        if dist not in diz_dis_freq.keys():
                            diz_dis_freq[dist] = 0
                        diz_dis_freq[dist] += f.result()[dist]
                    #distTemp.write(json.dumps(f.result())+"\n")
                buffer.clear()
            else:
                listaRipetizioni = np.array(listaRipetizioni)
                distanze = calcola_distanze_match(listaRipetizioni)
                for dist in distanze.keys():
                    if dist not in diz_dis_freq.keys():
                        diz_dis_freq[dist] = 0
                    diz_dis_freq[dist] += distanze[dist]
                '''
                for i in range(len(listaRipetizioni) - 1):
                    for j in range(i, len(listaRipetizioni)):
                        if listaRipetizioni[j] > listaRipetizioni[i] + NUM_BASI_MER:
                            distanza = listaRipetizioni[j] - listaRipetizioni[i]
                            if distanza in temp:
                                temp[distanza] += 1
                            else:
                                temp[distanza] = 1
                '''
                #distTemp.write(json.dumps(temp)+"\n")

        nuoviBuffer = []
        nuovoBuffer = []
        chiaviBuffer = list(buffers.keys())
        i = len(chiaviBuffer) - 1
        while i >= 0:
            for j in buffers[chiaviBuffer[i]]:
                nuovoBuffer.append(j)
                if len(nuovoBuffer) == NUMERO_CORE:
                    nuoviBuffer.append(nuovoBuffer)
                    nuovoBuffer = []
            i = i - 1
        nuoviBuffer.append(nuovoBuffer)


        print(len(nuoviBuffer), "PRIMA: ", len(buffers))

        for buffer in nuoviBuffer:
            print(len(buffer))
            svuota_buffer(buffer, executor, diz_dis_freq)

        datiFinestra = DatiFinestra()
        datiFinestra.posIniziale = dimFinestre[cont]
        datiFinestra.posFinale = dimFinestre[cont] + len(nuove_finestre[cont])
        datiFinestra.numeroBasi = len(nuove_finestre[cont])
        datiFinestra.distanze = diz_dis_freq
        datiFinestra.entropiaShannon = entropy(np.array(list(diz_dis_freq.values())))
        datiFinestra.indiceSimpson = integrate.simpson(np.array(list(diz_dis_freq.values())))
        datiFinestra.numRipetizioni = cont_matches
        distDistanze.append(datiFinestra.__dict__)
        writer.writerow([datiFinestra.posIniziale, datiFinestra.posFinale, datiFinestra.numeroBasi, datiFinestra.entropiaShannon, datiFinestra.indiceSimpson, datiFinestra.numRipetizioni])


    with open(cartellaRisultati+"SavedFiles/Distanze/distanze_"+nomefile+".json", "w") as fl:
        json.dump(distDistanze, fl)
    #distTemp.close()
    #distTemp = open(cartellaRisultati+"/distanze_temp_"+nomefile+".txt", "r")
    '''
    dizionari = distTemp.readlines()

    
    #Prendi dizionario dal disco e metti tutto insieme
    for dizionario in dizionari:
        diz = {}
        diz = json.loads(dizionario)
        for chiave in diz.keys():
            if chiave not in diz_dis_freq:
                diz_dis_freq[chiave] = diz[chiave]
            else:
                diz_dis_freq[chiave] = diz_dis_freq[chiave] + diz[chiave]
    '''


    #ft.write("Tempo calcolo distanze match finestra " + str(cont+1) + ": " + str(end-start) + "\n")

#Da cancellare
def match_pattern(app1, app2, distanza_frequente):
    if app1 == app2:
        return True
    else:
        caratteri_diversi = 0
        j = 0
        while j < len(app1) and j < len(app2):
            if app1[j] != app2[j]:
                caratteri_diversi = caratteri_diversi + 1
            j = j + 1
        if len(app1) != len(app2):
            if len(app1) > len(app2):
                caratteri_diversi = caratteri_diversi + (len(app1) - len(app2))
            else:
                caratteri_diversi = caratteri_diversi + (len(app2) - len(app1))
        if caratteri_diversi <= (distanza_frequente/3):
            return True
        else:
            return False

'''
----------------------------------------------------------------------------------------------
calcola_distanze_match calcola la distanza tra i match di uno stesso k-mer.               
Prende in input una lista contenente le posizioni finali di tutte le occorrenze           
del k-mer presenti all'interno del file contenente il cromosoma.                          
Restituisce in output un dizionario contenente come chiavi le diverse distanze calcolate  
e come valori la frequenza della distanza (il numero di volte in cui è stata trovata)     
----------------------------------------------------------------------------------------------
'''
def calcola_distanze_match(listaRipetizioni):
    risultato = {}

    for i in range(1, len(listaRipetizioni)):
        rip = listaRipetizioni[:i]
        rip = rip[listaRipetizioni[i] - rip <= 10000]
        distanze = listaRipetizioni[i] - rip
        distanze = distanze[distanze > 0]
        #distanze = distanze[distanze < 10000]

        for distanza in distanze:
            distanza = int(distanza)
            risultato[distanza] = risultato.get(distanza, 0) + 1

    return risultato


#Da cancellare
def calcola_match_singolo(listaRipetizioni, r):
    risultato = {}

    for i in r:
        rip = listaRipetizioni[:i]
        rip = rip[listaRipetizioni[i] - rip <= 10000]
        distanze = listaRipetizioni[i] - rip
        distanze = distanze[distanze > 0]
        #distanze = distanze[distanze < 10000]

        for distanza in distanze:
            distanza = int(distanza)
            if distanza not in risultato.keys():
                risultato[distanza] = 0
            risultato[distanza] += 1
    return risultato


'''
----------------------------------------------------------------------------------------------
gestisci_buffer si occupa della gestione di una lista di liste(buffer) di posizioni finali 
(che sono poi gestite attraverso calcola_match). Prende in input il buffer, l'esecutore per
il multiprocessing (concurrent.futures.ProcessPoolExecutor()), un file in scrittura per scrivere
i risultati su disco (per evitare di riempire la ram) e il numero core della macchina su
cui viene eseguito il codice
----------------------------------------------------------------------------------------------
'''
def gestisci_buffer(buffer, executor, distanze):
    numero_core = multiprocessing.cpu_count()
    if(len(buffer) == numero_core):
        print("SI")
        for k in buffer:
            print(len(k))
        results = [executor.submit(calcola_distanze_match, k) for k in buffer]
        for f in concurrent.futures.as_completed(results):
            for dist in f.result().keys():
                distanze[dist] = distanze.get(dist, 0) + f.result()[dist]
            '''
            print("RISULTATO")
            for chiave in f.result().keys():
                if chiave not in diz_dis_freq:
                    diz_dis_freq[chiave] = f.result()[chiave]
                else:
                    diz_dis_freq[chiave] = diz_dis_freq[chiave] + f.result()[chiave]
            '''
            #Dump dizionario
        buffer.clear()
'''
----------------------------------------------------------------------------------------------
svuota_buffer si occupa di gestire le ultime liste di posizioni finali di k-mer presenti
all'interno del file del cromosoma che non sono state gestite da gestisci_buffer poichè il 
buffer per poter essere gestito da gestisci_buffer deve essere pieno(il numero di liste
delle posizioni finali deve essere uguale al numero di core della macchina).
Prende in input il buffer, l'esecutore(concurrent.futures.ProcessPoolExecutor()) e un file 
in scrittura per scrivere i risultati su disco (per evitare di riempire la ram)
----------------------------------------------------------------------------------------------
'''
def svuota_buffer(buffer, executor, distanze):
    if(len(buffer) > 0):
        results = [executor.submit(calcola_distanze_match, k) for k in buffer]
        print("STO USANDO IL BUFFER PER L'ULTIMA VOLTA")
        for f in concurrent.futures.as_completed(results):
            for dist in f.result().keys():
                distanze[dist] = distanze.get(dist, 0) + f.result()[dist]
            '''
            for chiave in f.result().keys():
                if chiave not in diz_dis_freq:
                    diz_dis_freq[chiave] = f.result()[chiave]
                else:
                    diz_dis_freq[chiave] = diz_dis_freq[chiave] + f.result()[chiave]
            '''
            #Dump dizionario
        buffer.clear()

'''
----------------------------------------------------------------------------------------------
individua_e_gestisci_sovrapposizioni: da aggiustare e commentare
----------------------------------------------------------------------------------------------
'''
def individua_e_gestisci_sovrapposizioni(cont, posizioni_iniziali_match, posizioni_finali_match, nuove_finestre):
    match = []
    f1 = open('sequenze_da_allineare'+str(cont+1)+'.fna', "w")
    i = 0
    while i < (len(posizioni_iniziali_match)-1):
        j = i + 1
        p_i = 0
        p_f = 0
        trovata_s = False
        while j < len(posizioni_iniziali_match):
            if posizioni_iniziali_match[i] == posizioni_iniziali_match[j] and posizioni_finali_match[i] == posizioni_finali_match[j]:
                p_i = posizioni_iniziali_match[i]
                p_f = posizioni_finali_match[i]
            elif posizioni_finali_match[i] > posizioni_iniziali_match[j] and posizioni_iniziali_match[j] > posizioni_iniziali_match[i]:
                p_i = posizioni_iniziali_match[j]
                p_f = posizioni_finali_match[i]
            elif posizioni_finali_match[j] > posizioni_iniziali_match[i] and posizioni_iniziali_match[i] > posizioni_iniziali_match[j]:
                p_i = posizioni_iniziali_match[i]
                p_f = posizioni_finali_match[j]
            else:
                p_i = -1
                p_f = -1
            if p_i != -1:
                trovata_s = True
                if (p_f - p_i) < 10:
                    mezzo = int((p_i + p_f)/2)
                    if p_i < posizioni_iniziali_match[i]:
                        match.append(nuove_finestre[mezzo:posizioni_finali_match[i]])
                        match.append(nuove_finestre[posizioni_iniziali_match[j]:mezzo])
                    else:
                        match.append(nuove_finestre[mezzo:posizioni_finali_match[j]])
                        match.append(nuove_finestre[posizioni_iniziali_match[i]:mezzo])
                else:
                    if p_i < posizioni_iniziali_match[i]:
                        match.append(nuove_finestre[p_f:posizioni_finali_match[i]])
                        match.append(nuove_finestre[posizioni_iniziali_match[j]:p_f])
                    else:
                        match.append(nuove_finestre[p_i:posizioni_finali_match[j]])
                        match.append(nuove_finestre[posizioni_iniziali_match[i]:p_i])
            j = j + 1
        if trovata_s == False:
            match.append(nuove_finestre[posizioni_iniziali_match[i]:posizioni_finali_match[i]])
        i = i + 1
    k = 0
    while k < len(match):
        if match[k] != '':
            f1.write(">"+str(k+1)+'\n'+match[k]+'\n')
        k = k + 1
    del match
    f1.close()

'''
gestisci_cartelle: crea le directory necessarie per il salvataggio dei risultati
'''
def gestisci_cartelle(nomefile):
    cartellaRisultati = "risultati/"+nomefile+"/"
    Path(cartellaRisultati).mkdir(parents=True, exist_ok=True)
    Path(cartellaRisultati+"/Test").mkdir(parents=True, exist_ok=True)
    Path(cartellaRisultati+"/SavedFiles").mkdir(parents=True, exist_ok=True)
    Path(cartellaRisultati+"/SavedFiles/Distanze").mkdir(parents=True, exist_ok=True)
    return cartellaRisultati

'''
----------------------------------------------------------------------------------------------
mostra_alte_ripetizioni: da aggiustare e commentare
----------------------------------------------------------------------------------------------
'''
def mostra_alte_ripetizioni(cromosoma):

    cartellaRisultati = "risultati/"+cromosoma+"/"
    with open(cartellaRisultati+"SavedFiles/visualizzatore_"+cromosoma+".json", "r") as fl:
        visualizzatore_cromosoma = json.load(fl)

    esadecimali = {"0":"0", "1": "1", "2":"2", "3":"3", "4":"4", "5":"5", "6":"6", "7":"7", "8":"8", "9":"9", "10":"A", "11":"B", "12":"C", "13":"D", "14":"E", "15":"F"}

    opacita = []
    for i in range(len(visualizzatore_cromosoma)):
        numero = int(255 * abs(1 - visualizzatore_cromosoma[i]/1000))
        colore = "#" + ("{:x}{:x}{:x}").format(numero, numero, numero)
        opacita.append(colore)
        visualizzatore_cromosoma[i] = 1

    '''for i in range(len(visualizzatore_cromosoma)):
        if visualizzatore_cromosoma[i] > 1000/precisione:
            visualizzatore_cromosoma[i] = 1
        else:
            visualizzatore_cromosoma[i] = 0'''

    coloreFinestreAltaRipetizione = mpatches.Patch(color="#000000", label="Massima ripetitività")
    coloreFinestreBassaRipetizione = mpatches.Patch(color="#EEEEEE", label="Nessuna ripetitività")

    figura, grafico = plt.subplots()
    grafico.set_title("Ripetitività per blocchi da 1000 finestre del "+cromosoma)
    grafico.set_xlabel("Milioni di base pair")
    figura.set_figwidth(9)
    figura.set_figheight(2)
    figura.tight_layout()
    figura.legend(handles=[coloreFinestreAltaRipetizione, coloreFinestreBassaRipetizione], facecolor="#777777")
    grafico.set_ylim([0, 1])
    figura.gca().axes.get_yaxis().set_visible(False)
    grafico.xaxis.set_major_formatter('{x}Mbp')
    grafico.bar(x=np.arange(len(visualizzatore_cromosoma)), height=visualizzatore_cromosoma, color=opacita, align="edge", width=1)
    figura.savefig(cartellaRisultati+'centromero_'+cromosoma+'.jpg')
    figura.show()

'''
----------------------------------------------------------------------------------------------
mostra_istogramma: da aggiustare e commentare
----------------------------------------------------------------------------------------------
'''
def mostra_istogramma(cromosoma, numeroFinestreStampate, entropiaMax, entropiaMin, simpsonMin):
    cartellaRisultati = "risultati/"+cromosoma+"/"

    with open(cartellaRisultati+"SavedFiles/Distanze/distanze_"+cromosoma+".json", "r") as fl:
        finestre = json.load(fl)

    numeroFinestra = 0
    for finestra in finestre:
        chiavi = list(finestra["distanze"].keys())
        for i in range(len(chiavi)):
            chiavi[i] = int(chiavi[i])
        condizione = (max(chiavi) / 10000) * finestra["entropiaShannon"]
        if condizione < entropiaMax and condizione > entropiaMin and numeroFinestra < numeroFinestreStampate and finestra["indiceSimpson"] > simpsonMin:
            numeroFinestra = numeroFinestra + 1
            diz_dis_freq = finestra["distanze"]
            label = str(finestra["posIniziale"]) + ", " + str(finestra["posFinale"])
            Istogrammatore(diz_dis_freq, label)
        '''
        #distanza_frequente = max(diz_dis_freq, key=diz_dis_freq.get)

        limitex = 10000
        #limitey = 1000000
        x = np.array([int(dist) for dist in diz_dis_freq.keys()])

        numMaxValori = 10
        massimiX = []
        massimiY = []
        #valoreMax = 0
        for i in range(numMaxValori):
            massimiX.append(0)
            massimiY.append(0)
        valoriDizionario = list(diz_dis_freq.values())
        valoriDizionario.sort(reverse=True)
        massimiY = valoriDizionario[0:numMaxValori]
        for i in range(numMaxValori):
            for j in diz_dis_freq.keys():
                if diz_dis_freq[j] == massimiY[i]:
                    massimiX[i] = int(j)
                    break

        limitey = max(massimiY) + 5000

        figura, grafico = plt.subplots(figsize=(15, 10))
        grafico.set_xlim([0, limitex])
        grafico.set_ylim([0, limitey])

        grafico.bar(x=x, height=list(diz_dis_freq.values()), fc="orange", width = 5)
        grafico.set_xlabel("Valori distanza")
        grafico.set_ylabel("Valori frequenza")
        grafico.set_title("Istogramma frequenza distanze "+ chiave)

        annotation = grafico.annotate(
            text = '',
            xy = (0,0),
            xytext = (15,15),
            textcoords='offset points',
            bbox = {'boxstyle': 'round', 'fc': 'w'},
            arrowprops= {'arrowstyle': '->'}
        )
        annotation.set_visible(False)


        for i in range(numMaxValori):
            grafico.annotate(
                text = 'Picco: '+'({:.2f}, {:.2f})'.format(massimiX[i], massimiY[i]),
                xy = (massimiX[i], massimiY[i]),
                xytext = (15,15),
                textcoords='offset points',
                bbox = {'boxstyle': 'round', 'fc': 'w'},
                arrowprops= {'arrowstyle': '->'}
            )

        #cursor = Cursor(grafico, horizOn=True, vertOn=True, useblit=True, color = 'r', linewidth= 1)


        def onclick(event):
            raggioAzione = 20
            xcoord = event.xdata
            maxX = 0
            maxY = 0
            if raggioAzione > 0:
                for k in range(int(xcoord) - raggioAzione, int(xcoord) + raggioAzione):
                    if str(k) in diz_dis_freq.keys():
                        if maxY < diz_dis_freq[str(k)]:
                            maxY = diz_dis_freq[str(k)]
                            maxX = k
            else:
                maxY = diz_dis_freq[str(int(xcoord))]
                maxX = int(xcoord)
            annotation.xy = (maxX,maxY)
            text_label = '({:.2f}, {:.2f})'.format(maxX, maxY)
            annotation.set_text(text_label)
            annotation.set_visible(True)
            figura.canvas.draw()

        figura.canvas.mpl_connect('button_press_event', onclick)
        figura.show()
        numeroFinestra += 1'''