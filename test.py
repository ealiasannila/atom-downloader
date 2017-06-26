import numpy as np
import csv
usb_keys = np.genfromtxt('usb_interaktiivinen_laser.csv', delimiter=' ', dtype=None, usecols = [0])
usb_attrs = np.genfromtxt('usb_interaktiivinen_laser.csv', delimiter=' ', dtype=None, usecols = [1,2,4])
atom_keys = np.genfromtxt('atom_feed_laser.csv', delimiter=';', dtype=None ,usecols = [0])
atom_attrs = np.genfromtxt('atom_feed_laser.csv', delimiter=';', dtype=str ,usecols = [3,5])

atom_attrs[:,1] = [row[:-3] for row in atom_attrs[:,1]]


d_usb = dict(zip(usb_keys, usb_attrs.tolist()))
d_atom = dict(zip(atom_keys, atom_attrs.tolist()))

for k in d_atom:    
	d_usb[k] = np.append(d_usb[k],d_atom[k])

with open('combined_laser.csv', 'w') as csv_file:
    for key, value in d_usb.items():
    	csv_file.write(key)
	for v in value:
		csv_file.write(';' + str(v))
	csv_file.write('\n')


