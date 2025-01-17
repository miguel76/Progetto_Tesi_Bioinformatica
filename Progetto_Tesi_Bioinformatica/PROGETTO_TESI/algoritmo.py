import matplotlib.pyplot as plt

#import random
import re
import numpy as np
#import math
import multiprocessing
#from ClasseRisultato import RisultatoCalcoloMatch
import time
#import _pickle as pickle
import json
import FunzioniBio

NUMERO_CORE = multiprocessing.cpu_count()
LIMITE_SINGLE_CORE = 10000
NUM_BP_FINESTRA = 1000
NUM_SEQUENZE = 5
NUM_BASI_MER = 12
PERCENTUALE = 0.1
DIVISORE_GRAFICO_RIPETIZIONI = 1000
MAX_LIMITE_X = 10000

if __name__ == "__main__":
    cromosomi = ["cromosoma13"]
    estensione = ".fna"
    #for i in range(13):
    #    cromosomi.append("cromosoma"+str(i+1))
    nuoveFinestreCalcolate = False
    distanzeCalcolate = False
    graficoFatto = True
    voglioGraficoIllimitato = False
    voglioGraficoLimitato = False
    abilitaFileDebug = True
    saltaGrafico = True
    for nomefile in cromosomi:
        cartellaRisultati = FunzioniBio.gestisci_cartelle(nomefile)
        if abilitaFileDebug:
            ftt = open(cartellaRisultati+'Test/filetempi_overlap_multithread'+nomefile+'.txt', 'w')
        if(not nuoveFinestreCalcolate):
            cromosoma = FunzioniBio.caricaCromosoma(nomefile, estensione)
            start = time.time()
            print(len(cromosoma))
            print("Sto qua 1")
            #suddivisione del cromosoma in finestre da 1kbp = 1000 basi azotate
            finestra = FunzioniBio.suddivisioneCromosomaInFinestre(cromosoma)
            print(len(finestra))
            end = time.time()
            if abilitaFileDebug:
                ftt.write("Tempo suddivisione finestre: " + str(end-start) + "\n")

            # suddivisione delle finestre in 12-mers
            start = time.time()
            print("Sto qua 2")
            finestre_mers = FunzioniBio.suddivisioneFinestreInMers(finestra)
            end = time.time()
            if abilitaFileDebug:
                ftt.write("Tempo suddivisione finestre in 12-mers: " + str(end-start) + "\n")

            start = time.time()
            #matches = []
            print("Sto qua 3")
            #calcolo matches dei mers per ogni finestra
            matches_finestra = FunzioniBio.calcoloMatch(finestre_mers)
            end = time.time()
            if abilitaFileDebug:
                ftt.write("Tempo matches finestre: " + str(end-start) + "\n")

            #ricalcolo finestre in base al numero di mathces
            start = time.time()
            print("Sto qua 4")
            pos = FunzioniBio.ricalcoloFinestre(cartellaRisultati, nomefile, cromosoma, finestre_mers, matches_finestra)

            #dump visualizzatore_cromosoma

            #creazione delle nuove finestre
            FunzioniBio.creazioneNuoveFinestre(cartellaRisultati, nomefile, finestra, pos)

            #dump nuove_finestre
            end = time.time()
            if abilitaFileDebug:
                ftt.write("Tempo ricalcolo finestre: " + str(end-start) + "\n")
            #del mers
            del finestre_mers
            del finestra
            del matches_finestra

        if not saltaGrafico:
            FunzioniBio.mostra_alte_ripetizioni(nomefile, 4)

        if(not distanzeCalcolate):
            start = time.time()
            FunzioniBio.calcoloDistanzeMatch(cartellaRisultati, nomefile)
            end = time.time()
            if abilitaFileDebug:
                ftt.write("Tempo calcolo distanze match finestre: " + str(end-start) + "\n")
        '''
        #creazione istogramma similarita" media di ciscuna finestra
        if not graficoFatto:
            with open(cartellaRisultati+"SavedFiles/"+nomefile, "r") as fl:
                distanze = json.load(fl)
            cont = 1
            for diz_dis_freq in distanze:
                if not saltaGrafico:
                    if voglioGraficoLimitato:
                        distanza_frequente = max(diz_dis_freq, key=diz_dis_freq.get)

                        if limitey > diz_dis_freq[distanza_frequente]:
                            limitey = diz_dis_freq[distanza_frequente]

                        x = np.array([int(dist) for dist in diz_dis_freq.keys()])
                        yaxis = [int(dist) for dist in diz_dis_freq.values()]

                        x = x[x <= limitex]
                        yaxis = yaxis[:limitex]
                        y = []
                        for val in yaxis:
                            if val > limitey:
                                val = limitey
                            y.append(val)

                        figura, grafico = plt.subplots()
                        grafico.set_xlim([0, limitex])
                        grafico.set_ylim([0, limitey])

                        plt.figure(dpi=1200)
                        grafico.bar(x=x, height=y, fc="orange")
                        grafico.set_xlabel("Valori distanza")
                        grafico.set_ylabel("Valori frequenza")
                        grafico.set_title("Istogramma frequenza distanze")
                        #figura.text(int(distanza_frequente) + 12, int(diz_dis_freq[distanza_frequente]) + 12, "Distanza con frequenza maggiore: " + str(distanza_frequente))
                        #cerchio = Circle((int(distanza_frequente), int(diz_dis_freq[distanza_frequente])), 3, color="red", lw=3, fill= False, zorder=10)
                        #figura.gca().add_patch(cerchio)
                        figura.savefig(cartellaRisultati+'istogramma_parziale_'+nomefile+'.pdf')
                        figura.show()

                    if voglioGraficoIllimitato:
                        x = [int(dist) for dist in diz_dis_freq.keys()]
                        y = [int(dist) for dist in diz_dis_freq.values()]
                        figura, grafico = plt.subplots()
                        distanza_frequente = max(diz_dis_freq, key=diz_dis_freq.get)
                        plt.figure(dpi=1200)
                        grafico.bar(x=x, height=y, fc="orange")
                        grafico.set_xlabel("Valori distanza")
                        grafico.set_ylabel("Valori frequenza")
                        grafico.set_title("Istogramma frequenza distanze")
                        #figura.text(int(distanza_frequente) + 12, int(diz_dis_freq[distanza_frequente]) + 12, "Distanza con frequenza maggiore: " + str(distanza_frequente))
                        #cerchio = Circle((int(distanza_frequente), int(diz_dis_freq[distanza_frequente])), 3, color="red", lw=3, fill= False, zorder=10)
                        #figura.gca().add_patch(cerchio)
                        figura.savefig(cartellaRisultati+'istogramma_'+nomefile+"_"+str(cont)+'.pdf')
                        figura.show()

                cont = cont + 1
                #trovare distanza più frequente
                distanza_frequente = max(diz_dis_freq, key=diz_dis_freq.get)
                print("Distanza con frequenza maggiore: ", distanza_frequente)
                print("Frequenza della distanza: ", diz_dis_freq[distanza_frequente])
                distanza_frequente = int(distanza_frequente)
        '''
        '''
        #generazione 5 sequenze random di lunghezza N pari alla distanza più frequente
        i = 0
        sequenze = []
        sequenze_regioni = []
    
        for cont in range(0, len(nuove_finestre)):
            sequenze = []
            print("STO QUA VITO: " + str(cont) + " su: " + str(len(nuove_finestre)))
            for i in range(0, NUM_SEQUENZE):
                limite = len(nuove_finestre[cont]) - distanza_frequente
                numero_casuale = random.randrange(0, limite)
                seq = []
                for j in range(0, distanza_frequente):
                    seq.append(nuove_finestre[cont][numero_casuale])
                    numero_casuale = numero_casuale + 1
                sequenze.append("".join(seq))
            sequenze_regioni.append(sequenze)
        print("Sequenze generate", sequenze_regioni)
        start = time.time()
        #match delle sequenze generate con la regione di interesse
        pos_in = []
        pos_fin = []
        posizioni_iniziali_match = []
        posizioni_finali_match = []
    
        for cont in range(0, len(nuove_finestre)):
            print("STO QUA MICHELE: " + str(cont) + " su: " + str(len(nuove_finestre)))
            for k in range(0, NUM_SEQUENZE):
                for i in range(0, (len(nuove_finestre[cont]) - distanza_frequente)):
                    p_i = i
                    p_f = i + distanza_frequente
                    if match_pattern(sequenze_regioni[cont][k], nuove_finestre[cont][p_i:p_f], distanza_frequente):
                        pos_in.append(p_i)
                        pos_fin.append(p_f)
            posizioni_iniziali_match.append(pos_in)
            posizioni_finali_match.append(pos_fin)
        end = time.time()
        #ft.write("Tempo match tra sequenze e regioni di interesse: " + str(end-start) + "\n")
        #individuazione e gestione delle sovrapposizioni
        contrange = NUMERO_CORE
        executor = concurrent.futures.ThreadPoolExecutor()
        start = time.time()
        cont = range(0,contrange)
        while cont[NUMERO_CORE - 1] < len(nuove_finestre):
            print("STO FINENDO")
            [executor.submit(individua_e_gestisci_sovrapposizioni, k, posizioni_iniziali_match[k], posizioni_finali_match[k], nuove_finestre[k]) for k in cont]
            cont = range(contrange, contrange + NUMERO_CORE)
            contrange = contrange + NUMERO_CORE
        if(cont[0] < (len(nuove_finestre))):
            cont = range(cont[0], len(nuove_finestre))
            [executor.submit(individua_e_gestisci_sovrapposizioni, k, posizioni_iniziali_match[k], posizioni_finali_match[k], nuove_finestre[k]) for k in cont]
        end = time.time()
        #ft.write("Tempo individuazione e gestione overlap: " + str(end-start) + "\n")
        '''