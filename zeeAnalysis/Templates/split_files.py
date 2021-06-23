#!/bin/python

with open('DYToEE_selected_event_list.txt', 'r') as input_f:
    evtlist = input_f.readlines()

nevts = len(evtlist)
print('N evts:',nevts)

nfiles = 5
print('N files to split over:',nfiles)

nbatch = nevts//nfiles
print('N evts / file:',nbatch)

for f in range(nfiles):

    start = f*nbatch
    stop = (f+1)*nbatch if f < nfiles-1 else nevts
    print(f, start, stop)

    output_f = open('DYToEE%d_selected_event_list.txt'%f, 'w')

    for i in range(start, stop):
        output_f.write(evtlist[i])

    output_f.close()
