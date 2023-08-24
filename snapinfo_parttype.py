import h5py
import argparse
from sys import argv

'''
snapinfo_parttype.py

Print information about a GADGET HDF5 snapshot for a specific PartType.

Usage:

python3 snapinfo_parttype.py input PartType

where PartType is one of ['PartType0', 'PartType1', 'PartType2', 'PartType3', 'PartType4']

'''

def main(snapshot, requested_part_type):
    valid_part_types = ['PartType0', 'PartType1', 'PartType2', 'PartType3', 'PartType4']
    if requested_part_type not in valid_part_types:
        print(f"Invalid PartType: {requested_part_type}. Please choose from {valid_part_types}.")
        exit()

    with h5py.File(snapshot, 'r') as f:
        header = f['Header'].attrs
        time = header['Time']
        print('time   = %f' % time)

        if requested_part_type in f:
            group = f[requested_part_type]
            
            keys = list(group.keys())
            for key in keys:
                print(f"\n{key} = {group[key][:]}")
        else:
            print(f"{requested_part_type} not found in the snapshot.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Print information about a GADGET HDF5 snapshot for a specific PartType.")
    parser.add_argument("input", help="Path to the input HDF5 snapshot")
    parser.add_argument("PartType", choices=['PartType0', 'PartType1', 'PartType2', 'PartType3', 'PartType4'], 
                        help="Particle type to retrieve information for")
    
    args = parser.parse_args()
    main(args.input, args.PartType)