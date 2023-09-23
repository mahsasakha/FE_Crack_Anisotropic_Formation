import csv
import math
from numpy import *
from subprocess import call
import datetime
import os

import matplotlib.pyplot as plt

#Run_adpl has been taken from https://mechanicsandmachines.com/?p=581
def run_apdl(ansyscall, numprocessors, workingdir, script_filename):
    """
    runs the APDL script: scriptFilename.inp
    located in the folder: workingdir
    using APDL executable invoked by: ansyscall
    using the number of processors in: numprocessors
    returns the number of Ansys errors encountered in the run
    """
    input_file = os.path.join(workingdir,
                              script_filename + ".txt")
    # make the output file be the input file plus timestamp
    output_file = os.path.join(workingdir,
                               script_filename +
                               '{:%Y%m%d%H%M%S}'.format(datetime.datetime.now()) +
                               ".out")
    # keep the standard ansys jobname
    jobname = "file"
    call_string = ("\"{}\"-p ansys  -smp"
                   " -np {} -dir \"{}\" -j \"{}\" -s read"
                   " -b -i \"{}\" -o \"{}\"").format(
        ansyscall,
        numprocessors,
        workingdir,
        jobname,
        input_file,
        output_file)
    print("invoking ansys with: ", call_string)
    call(call_string, shell=False)

    # check output file for errors
    print("checking for errors")
    numerrors = "undetermined"
    try:
        searchfile = open(output_file, "r")
    except:
        print("could not open", output_file)
    else:
        for line in searchfile:
            if "NUMBER OF ERROR" in line:
                print(line)
                numerrors = int(line.split()[-1])
        searchfile.close()
    return numerrors


E_prim = 18 #Weak direction, GPa
xi = 5 #Ratio of E/E_prim
sigma_1 = 5.619 #Tensile strength along the weak direction, MPa
wellbore_size = 80/1000 #mm --> m
Unit = 1000

#  g_theta =
# ((1.56*(math.cos(theta)**2)+1.56*xi*(math.sin(theta)**2))**2)*((xi+math.sqrt(xi))*(math.cos(theta)**2)+
# (1+math.sqrt(xi))*(math.sin(theta)**2))/(2*E_prim*xi*0.001)


orientation = (89, 60,45,30,15,0) # Orientation of the isotropy plan


def main():
    os.chdir(r"C:\path\to\DATA\MATERIAL_5")
    old_step = zeros(6)
    new_step = ones(6)
    while sum(old_step) < sum(new_step):
        file = open("Initiation_Pressure.csv")
        csvreader = csv.reader(file)

        pressure_updated =[]
        for row in csvreader:

            if float(row[1]) > 0:
                column_updated = [float(row[1]) - min(0.005, old_step[int(row[0])]) *
                                  (new_step[int(row[0])] - old_step[int(row[0])]) * float(row[1])]
                pressure_updated.append(column_updated)

        file.close()
        row_0 = ['', 0, 1]
        # then you write the updated pressure into the same file
        with open('Initiation_Pressure.csv', 'w', encoding='UTF8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(row_0)

        for i in range(0, 6, 1):
            data = pressure_updated[i]
            with open('Initiation_Pressure.csv', 'a+', encoding='UTF8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([i, data[0], 1])
        with open('Initiation_Pressure_vec.csv', 'w', encoding='UTF8', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(pressure_updated)

        ansyscall = "C:\\Program Files\\path\\to\\MAPDL.exe"
        numprocessors = 8
        workingdir = "C:\\path\\to\\MATERIAL_5"
        script_filename = "APDL"
        n_err = run_apdl(ansyscall,
                         numprocessors,
                         workingdir,
                         script_filename)
        os.chdir(r"C:\path\to\DATA\MATERIAL_5")

        distance_of_path = range(1, 29, 1)
        output = []
        for i in orientation:
            data_max_sigma = []
            data_theta = []
            data_length = []
            for j in distance_of_path:
                file = open("Normal_stress_%d_%d.csv" % (i, j))
                csvreader = csv.reader(file)
                data_translated = []
                for row in csvreader:
                    row_translated = [float(row[1]) / float(row[0]) * (180 / math.pi) - 90, float(row[2]) / 1e6]
                    theta = math.pi * (row_translated[0] - i) / 180
                    sigma_theta = (sigma_1 * (math.cos(theta) ** 2) + sigma_1 * xi * (math.sin(theta) ** 2))
                    row_translated[1] = row_translated[1] / sigma_theta
                    data_translated.append(row_translated)
                data_length.append(float(row[0]))

                file.close()

                index = where(data_translated == amax(data_translated, axis=0))
                index_max = index[0]
                data_of_max = data_translated[index_max[0]]
                data_theta.append(data_of_max[0])
                data_max_sigma.append(data_of_max[1])

            print('At the material orientation of', i, 'degrees,',
                  'for all of the path set, we found the maximum of hoop stress as follows:',
                  data_max_sigma)

            index = where((logical_and(asarray(data_max_sigma) > 1 - 0.009, asarray(data_max_sigma) < 1 + 0.04)))

            index_unity = amin(index)
            print(index_unity)

            print('At the material orientation of', i, 'degrees,',
                  'at the distance of', data_length[index_unity], 'away from the center, giving the delta_0 of:',
                  (data_length[index_unity] - wellbore_size) / wellbore_size,
                  ', there is a crack tip along:',
                  data_theta[index_unity], 'degrees')
            output.append([i, data_length[index_unity]*Unit, ceil(data_theta[index_unity])])
        print('In aggregate:')
        print(output)

        f = open("Initiation_Pressure_vec.csv")
        existing = csv.reader(f)

        i = 0
        # first you have to read in your existing rows/cols
        for row in existing:
            output[i].append(float(row[0]))
            i += 1
        output = fliplr(output)
        f.close()
        # then you transpose it to get your columns
        with open('Initiation_parameters_All88.csv', 'w', encoding='UTF8', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(output)

        script_filename = "APDL_Crack_Wellbore"
        # first you have to read in your existing rows/cols
        result = []
        counter = 0
        for row in output:
            row_1 = [0]
            row_0 = ['', 0, 1, 2, 3]
            row_list = list(row)
            row_1 += list(row)
            row_2 = [1, 1, 1, 1, 1]
            rows = [row_0, row_1, row_2]
            with open('Initiation_parameters.csv', 'w', newline='') as file:
                mywriter = csv.writer(file, delimiter=',')
                mywriter.writerows(rows)
            n_err = run_apdl(ansyscall,
                             numprocessors,
                             workingdir,
                             script_filename)
            print("number of Ansys errors: ", n_err)
            f_cracked = open("Energy_Cracked_%d.csv" % (orientation[counter]))
            f_crack_free = open("Energy_Crack_free_%d.csv" % (orientation[counter]))
            reader_cracked = csv.reader(f_cracked)

            reader_crack_free = csv.reader(f_crack_free)
            for (read_1, read_2) in zip(reader_cracked, reader_crack_free):
                print((float(read_1[0])-0*float(read_2[0])))
                print((row_list[2]-wellbore_size*Unit))
                energy = (float(read_1[0])-float(read_2[0]))*1e3/(2*(row_list[2]-wellbore_size*Unit))
                if energy < 0:
                    print('there is an error due to negative energy release rate')

            theta = math.pi * (row_list[3] - row_list[1]) / 180
            g_theta = ((1.56 * (math.cos(theta) ** 2) + 1.56 * xi * (math.sin(theta) ** 2)) ** 2) * (
                    (xi + math.sqrt(xi)) * (math.cos(theta) ** 2) + (1 + math.sqrt(xi)) * (math.sin(theta) ** 2)) / (
                              2 * E_prim * xi * 0.001)
            row_list += [energy, g_theta]
            if energy-g_theta > 0.05 * g_theta:
                print('at the material orientation', orientation[counter], ', the energy diff is:', energy-g_theta)
                print(';And the 5% of toughness is :', 0.05 * g_theta)
                old_step[counter] = new_step[counter]
                new_step[counter] += 1
            else:
                print('at the material orientation', orientation[counter], ', the energy diff is:', energy-g_theta)
                print('which is negligible')
                old_step[counter] = new_step[counter]
            result.append(row_list)
            f_cracked.close()
            f_crack_free.close()
            counter += 1
        with open('Initiation_parameters_All88.csv', 'w', encoding='UTF8', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(result)

if __name__ == '__main__':
    main()
