import json

with open('notFinishedLumis.json') as f:
#with open('notFinishedLumis_test.json') as f:
    data = json.load(f)

print(data)

fout = open('notFinishedLumis.txt', 'w')
#fout = open('notFinishedLumis_test.txt', 'w')
for run,lumis in data.iteritems(): #py3: data.items()
    for lumi in lumis:
        #print(lumi)
        #print(lumi[0])
        #print(type(lumi[0]))
        #print(run)
        #print(type(run))
        run = int(run)
        #print('%d:%d-%d:%d'%(run, lumi[0], run, lumi[-1]))
        skip_lumi = '%d:%d-%d:%d\n'%(run, lumi[0], run, lumi[-1])
        fout.write(skip_lumi)
        #break

fout.close()
