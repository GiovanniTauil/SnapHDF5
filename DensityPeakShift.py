import h5py
import numpy as np
import argparse
from sys import argv
import unsiotools.simulations.cfalcon as falcon

def compute_density(x, y, z, m):
    """
    Computes the density of the particles using the falcon.CFalcon class.

    Parameters:
    x (array-like): x-coordinates of the particles.
    y (array-like): y-coordinates of the particles.
    z (array-like): z-coordinates of the particles.
    m (array-like): masses of the particles.

    Returns:
    dens (array-like): density of the particles.
    """
    # Check if input arrays have the same length
    if not (len(x) == len(y) == len(z) == len(m)):
        raise ValueError("Input arrays must have the same length.")

    # Build pos array
    pos = np.array([x, y, z])
    # Format required by UNS
    pos = pos.T.astype('float32').flatten()
    # Use falcon to get densities
    cf = falcon.CFalcon()
    _, dens, _ = cf.getDensity(pos, m)

    return dens

def find_peak(x, y, z, vx, vy, vz, m, Ndensest=64):
    """
    Finds the peak of the particles by selecting the densest particles and 
    calculating the average of their coordinates and velocities.

    Parameters:
    x (array-like): x-coordinates of the particles.
    y (array-like): y-coordinates of the particles.
    z (array-like): z-coordinates of the particles.
    vx (array-like): x-component of velocities of the particles.
    vy (array-like): y-component of velocities of the particles.
    vz (array-like): z-component of velocities of the particles.
    m (array-like): masses of the particles.
    Ndensest (int): Number of densest particles to select.

    Returns:
    tuple: Average positions (xpeak, ypeak, zpeak) and velocities (vxpeak, vypeak, vzpeak) of the densest particles.
    """
    # Call function to compute densities
    dens = compute_density(x, y, z, m)
    # Sort particles by decreasing density
    sort = np.argsort(dens)[::-1]
    x = x[sort]
    y = y[sort]
    z = z[sort]
    vx = vx[sort]
    vy = vy[sort]
    vz = vz[sort]
    dens = dens[sort]
    # Select a few of the densest particles
    # Average positions of the densest particles
    xpeak = np.average(x[0:Ndensest])
    ypeak = np.average(y[0:Ndensest])
    zpeak = np.average(z[0:Ndensest])
    # Average velocities of the densest particles
    vxpeak = np.average(vx[0:Ndensest])
    vypeak = np.average(vy[0:Ndensest])
    vzpeak = np.average(vz[0:Ndensest])

    return xpeak, ypeak, zpeak, vxpeak, vypeak, vzpeak
	
def main(input_snapshot, output_snapshot):
    with h5py.File(input_snapshot, 'r') as input_file:
        with h5py.File(output_snapshot, 'w') as output_file:
            input_header = input_file['Header']
            output_header = output_file.create_group('Header')
            for key, value in input_header.attrs.items():
                output_header.attrs[key] = value
            
            PartTypes = ['PartType0', 'PartType1', 'PartType2', 'PartType3', 'PartType4']
            
            all_pos = []
            all_vel = []
            all_mass = []

            for pt in PartTypes:
                if pt in input_file and 'Masses' in input_file[pt] and 'Coordinates' in input_file[pt] and 'Velocities' in input_file[pt]:
                    masses = input_file[pt]['Masses'][:]
                    pos = input_file[pt]['Coordinates'][:]
                    vel = input_file[pt]['Velocities'][:]
                    
                    all_mass.append(masses)
                    all_pos.append(pos)
                    all_vel.append(vel)

            all_mass = np.concatenate(all_mass)
            all_pos = np.concatenate(all_pos, axis=0)
            all_vel = np.concatenate(all_vel, axis=0)

            xpeak, ypeak, zpeak, vxpeak, vypeak, vzpeak = find_peak(all_pos[:, 0], all_pos[:, 1], all_pos[:, 2], 
                                                                     all_vel[:, 0], all_vel[:, 1], all_vel[:, 2], all_mass)

            for pt in PartTypes:
                if pt in input_file:
                    input_group = input_file[pt]
                    output_group = output_file.create_group(pt)
                    
                    if 'Coordinates' in input_group:
                        coords = input_group['Coordinates'][:]
                        coords[:, 0] -= xpeak
                        coords[:, 1] -= ypeak
                        coords[:, 2] -= zpeak
                        output_group.create_dataset('Coordinates', data=coords)
                    if 'Velocities' in input_group:
                        vels = input_group['Velocities'][:]
                        vels[:, 0] -= vxpeak
                        vels[:, 1] -= vypeak
                        vels[:, 2] -= vzpeak
                        output_group.create_dataset('Velocities', data=vels)
                    
                    for key in input_group.keys():
                        if key not in ['Coordinates', 'Velocities']:
                            data = input_group[key][:]
                            output_group.create_dataset(key, data=data)
                            
    print(f"Snapshot data shifted and saved from {input_snapshot} to {output_snapshot}.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reads a GADGET HDF5 snapshot, shifts positions and velocities to the center of mass, and writes the modified data to a new snapshot.")
    parser.add_argument("input", help="Path to the input HDF5 snapshot")
    parser.add_argument("output", help="Path to the output HDF5 snapshot")
    
    args = parser.parse_args()
    main(args.input, args.output)