#from posixpath import split

#f file contenente il genoma umano
f = open('D:/TESI/ncbi-genomes-2022-08-10/GCF_009914755.1_T2T-CHM13v2.0_genomic.fna')
genommaUmano = f.read()
i = 1
#fi saranno i file contenenti i cromosomi del genoma umano
cromosomi = genommaUmano.split('>')
while i < len(cromosomi):
    fi = open("D:/TESI/ncbi-genomes-2022-08-10/cromosoma"+str(i)+".fna", "w")
    fi.write(cromosomi[i].upper())
    fi.close()
    i = i + 1
























