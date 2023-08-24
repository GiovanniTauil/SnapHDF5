import h5py
import argparse
from sys import argv

'''
snapshot_copy_hdf5.py

Reads a GADGET HDF5 snapshot and creates another HDF5 snapshot with the read information.

Usage:

python3 snapshot_copy_hdf5.py input output

'''

def main(input_snapshot, output_snapshot):
    with h5py.File(input_snapshot, 'r') as input_file:
        with h5py.File(output_snapshot, 'w') as output_file:
            input_header = input_file['Header']
            output_header = output_file.create_group('Header')
            for key, value in input_header.attrs.items():
                output_header.attrs[key] = value
            
            PartTypes = ['PartType0', 'PartType1', 'PartType2', 'PartType3', 'PartType4']
            
            for pt in PartTypes:
                if pt in input_file:
                    input_group = input_file[pt]
                    output_group = output_file.create_group(pt)
                    
                    for key in input_group.keys():
                        data = input_group[key][:]
                        output_group.create_dataset(key, data=data)
                        
    print(f"Snapshot copied from {input_snapshot} to {output_snapshot}.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reads a GADGET HDF5 snapshot and creates another HDF5 snapshot with the read information.")
    parser.add_argument("input", help="Path to the input HDF5 snapshot")
    parser.add_argument("output", help="Path to the output HDF5 snapshot")
    
    args = parser.parse_args()
    main(args.input, args.output)