import h5py
import numpy as np
import argparse
from sys import argv

'''
shift_to_com_hdf5.py

Reads a GADGET HDF5 snapshot, shifts all positions and velocities to the centers of mass, 
and writes the modified data to a new snapshot.

Usage:

python3 shift_to_com_hdf5.py input output

'''

def compute_com(data, masses):
    return np.sum(data * masses[:, np.newaxis], axis=0) / np.sum(masses)

def main(input_snapshot, output_snapshot):
    with h5py.File(input_snapshot, 'r') as input_file:
        with h5py.File(output_snapshot, 'w') as output_file:
            input_header = input_file['Header']
            output_header = output_file.create_group('Header')
            for key, value in input_header.attrs.items():
                output_header.attrs[key] = value
            
            PartTypes = ['PartType0', 'PartType1', 'PartType2', 'PartType3', 'PartType4']
            
            total_mass = []
            total_pos = []
            total_vel = []

            for pt in PartTypes:
                if pt in input_file and 'Masses' in input_file[pt] and 'Coordinates' in input_file[pt] and 'Velocities' in input_file[pt]:
                    masses = input_file[pt]['Masses'][:]
                    pos = input_file[pt]['Coordinates'][:]
                    vel = input_file[pt]['Velocities'][:]
                    
                    total_mass.append(masses)
                    total_pos.append(pos)
                    total_vel.append(vel)

            total_mass = np.concatenate(total_mass)
            total_pos = np.concatenate(total_pos)
            total_vel = np.concatenate(total_vel)

            pos_com = compute_com(total_pos, total_mass)
            vel_com = compute_com(total_vel, total_mass)

            for pt in PartTypes:
                if pt in input_file:
                    input_group = input_file[pt]
                    output_group = output_file.create_group(pt)
                    
                    if 'Coordinates' in input_group:
                        coords = input_group['Coordinates'][:] - pos_com
                        output_group.create_dataset('Coordinates', data=coords)
                    if 'Velocities' in input_group:
                        vels = input_group['Velocities'][:] - vel_com
                        output_group.create_dataset('Velocities', data=vels)
                    
                    for key in input_group.keys():
                        if key not in ['Coordinates', 'Velocities']:
                            data = input_group[key][:]
                            output_group.create_dataset(key, data=data)
                            
    print(f"Snapshot data shifted and saved from {input_snapshot} to {output_snapshot}.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reads a GADGET HDF5 snapshot, shifts all positions and velocities to the centers of mass, and writes the modified data to a new snapshot.")
    parser.add_argument("input", help="Path to the input HDF5 snapshot")
    parser.add_argument("output", help="Path to the output HDF5 snapshot")
    
    args = parser.parse_args()
    main(args.input, args.output)
