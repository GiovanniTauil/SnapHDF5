import argparse
import h5py
from sys import argv

'''
snapinfo_hdf5.py

Print information about a GADGET HDF5 snapshot.

Usage:

python3 snapinfo_hdf5.py input

'''

def main(snapshot):
    with h5py.File(snapshot, 'r') as f:
        header = f['Header'].attrs
        time = header['Time']
        Npart = header['NumPart_ThisFile']
        
        print('time   = %f' % time)
        
        Comp = ['Gas', 'Halo', 'Disk', 'Bulge', 'Stars']
        PartType = ['PartType0', 'PartType1', 'PartType2', 'PartType3', 'PartType4']
        
        for i, comp in enumerate(Comp):
            if Npart[i] > 0:
                print('\n=================================')
                print(comp)
                print('=================================')
                group = f[PartType[i]]
                
                keys = list(group.keys())
                for key in keys:
                    print(f"\n{key} = {group[key][:]}")
        
        print('NTOTAL = %d ' % sum(Npart))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Print information about a GADGET HDF5 snapshot.")
    parser.add_argument("input", help="Path to the input HDF5 snapshot")
    
    args = parser.parse_args()
    main(args.input)

