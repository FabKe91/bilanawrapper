'''
    This module stores functions that write script files for various calculations
    They are used in __main__.py
    All functions must use the same keyword parameter names and the *args and **kwargs parameters as input
'''
import os
import subprocess

from bilana2 import Systeminfo

from .helperfunctions import get_minmaxdiv
from .slurm import write_submitfile
#from .common import write_submitfile
#from .common import get_minmaxdiv
#from .systeminfo import SysInfo

def submit_energycalcs(systemname, temperature, jobname, lipidpart, *args,
    inputfilename="inputfile",
    neighborfile="neighbor_info",
    startdivisor=80,
    overwrite=False,
    cores=2,
    dry=False,
    **kwargs,):
    ''' Divide energyruns into smaller parts for faster computation and submit those runs '''
    complete_name = './{}_{}'.format(systemname, temperature)
    os.chdir(complete_name)
    mysystem = Systeminfo(inputfilename)
    systemsize = mysystem.number_of_lipids
    divisor = get_minmaxdiv(startdivisor, systemsize)
    if divisor % 1 != 0:
        raise ValueError("divisor must be int")
    resids_to_calculate = list(mysystem.lipid_resids)
    lipids_per_part = systemsize // divisor
    print("System and temperature:", systemname, temperature)
    print("Will overwrite:", overwrite)
    print("Lipids per job:", lipids_per_part)
    for jobpart in range(divisor):
        list_of_res = resids_to_calculate[jobpart*lipids_per_part:(jobpart+1)*lipids_per_part]
        jobfile_name = str(jobpart)+'_'+jobname
        jobscript_name = 'exec_energycalc'+str(jobfile_name)+'.py'
        with open(jobscript_name, "w") as jobf:
            print(
                '\nimport os, sys'
                '\nimport bilana2 as bl'
                '\nfrom bilana2 import Energy'
                '\nneighbor_map = bl.neighbor.get_neighbor_dict(neighborfilename="{3}")'
                '\nenergy_instance = Energy("{0}", neighbor_map, overwrite={1}, inputfilepath="{2}")'
                '\nenergy_instance.run_calculation(resids={4})'
                '\nos.remove(sys.argv[0])'.format(lipidpart, overwrite, inputfilename, neighborfile, list_of_res),
                file=jobf)
        if not dry:
            write_submitfile('submit.sh', jobfile_name, ncores=cores)
            cmd = ['sbatch', '-J', complete_name[2:]+"_"+str(jobpart)+'_'+jobname, 'submit.sh','python3', jobscript_name]
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = proc.communicate()
            print(out.decode(), err.decode())

def submit_energycalc_leaflet(systemname, temperature, jobname, *args,
    inputfilename="inputfile",
    neighborfile="neighbor_info",
    startdivisor=80,
    overwrite=False,
    cores=2,
    dry=False,
    **kwargs,):
    ''' Divide energyruns into smaller parts for faster computation and submit those runs '''
    complete_name = './{}_{}'.format(systemname, temperature)
    os.chdir(complete_name)
    mysystem   = Systeminfo(inputfilename)
    systemsize = mysystem.number_of_lipids
    divisor = get_minmaxdiv(startdivisor, systemsize)
    if divisor % 1 != 0:
        raise ValueError("divisor must be int")
    resids_to_calculate = list(mysystem.lipid_resids)
    lipids_per_part     = systemsize//divisor
    print("System and temperature:", systemname, temperature)
    print("Will overwrite:", overwrite)
    print("Lipids per job:", lipids_per_part)
    for jobpart in range(divisor):
        list_of_res    = resids_to_calculate[jobpart*lipids_per_part:(jobpart+1)*lipids_per_part]
        jobfile_name   = str(jobpart)+'_'+jobname
        jobscript_name = 'exec_energycalc'+str(jobfile_name)+'.py'
        with open(jobscript_name, "w") as jobf:
            print(
                '\nimport os, sys'
                '\nimport bilana2 as bl'
                '\nfrom bilana2 import Energy'
                '\nneighbor_map = bl.neighbor.get_neighbor_dict(neighborfilename="{3}")'
                '\nenergy_instance = Energy("{0}", neighbor_map, overwrite={1}, inputfilepath="{2}")'
                '\nenergy_instance.run_lip_leaflet_interaction(resids={3})'
                '\nos.remove(sys.argv[0])'.format(overwrite, inputfilename, neighborfile, list_of_res),
                file=jobf)
        if not dry:
            write_submitfile('submit.sh', jobfile_name, ncores=cores)
            cmd = ['sbatch', '-J', complete_name[2:]+"_"+str(jobpart)+'_'+jobname, 'submit.sh','python3', jobscript_name]
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = proc.communicate()
            print(out.decode(), err.decode())

def submit_energycalc_on_res(systemname, temperature, jobname, lipidpart, resid, *args,
    inputfilename="inputfile",
    neighborfile="neighbor_info",
    cores=2,
    dry=False,
    **kwargs,):
    complete_name  = './{}_{}'.format(systemname, temperature)
    os.chdir(complete_name)
    print("System and temperature:", systemname, temperature)
    jobfile_name   = str(resid)+'_'+jobname
    jobscript_name = 'exec_energycalc'+str(jobfile_name)+'.py'
    with open(jobscript_name, "w") as jobf:
        print(
            '\nimport os, sys'
            '\nimport bilana2 as bl'
            '\nfrom bilana2 import Energy'
            '\nneighbor_map = bl.neighbor.get_neighbor_dict(neighborfilename="{3}")'
            '\nenergy_instance = Energy("{0}", neighbor_map, overwrite={1}, inputfilepath="{2}")'
            '\nenergy_instance.run_calculation(resids=[{3}])'
            '\nos.remove(sys.argv[0])'.format(lipidpart, inputfilename, neighborfile, resid),
            file=jobf)
    if not dry:
        write_submitfile('submit.sh', jobfile_name, ncores=cores)
        cmd = ['sbatch', '-J', complete_name[2:]+"_"+str(resid)+'_'+jobname, 'submit.sh','python3', jobscript_name]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = proc.communicate()
        print(out.decode(), err.decode())

def initialize_system(systemname, temperature, jobname, *args,
    inputfilename="inputfile",
    cores=16,
    prio=False,
    dry=False,
    mem='32G',
    **kwargs):
    ''' Creates all core files like neighbor_info, resindex_all, scd_distribution '''
    complete_systemname = './{}_{}'.format(systemname, temperature)
    os.chdir(complete_systemname)
    scriptfilename = 'exec'+complete_systemname[2:]+jobname+'.py'
    jobfilename = complete_systemname[2:]+"_"+jobname
    with open(scriptfilename, 'w') as scriptf:
        print(\
            'import os, sys'
            '\nimport bilana2'
            '\nfrom bilana2 import Systeminfo'
            '\nfrom bilana.core import neighbor'
            '\nfrom bilana.core import order'
            '\nsysinfo = bl.Systeminfo(inputfilepath="{0}")'
            '\nneighbor.write_neighbor_info(sysinfo)'
            '\nnenergy.create_indexfile(sysinfo)'
            .format(inputfilename),
            file=scriptf)
        if not dry:
            write_submitfile('submit.sh', jobfilename, mem=mem, ncores=cores, prio=prio)
            cmd = ['sbatch', '-J', jobfilename, 'submit.sh','python3', scriptfilename]
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = proc.communicate()
            print(out.decode(), err.decode())

def calc_scd(systemname, temperature, jobname, *args,
    inputfilename="inputfile",
    neighborfile="neighbor_info",
    dry=False,
    **kwargs,):
    ''' Only calculate scd distribution and write to scd_distribution.dat '''
    complete_systemname = './{}_{}'.format(systemname, temperature)
    os.chdir(complete_systemname)
    scriptfilename = 'exec'+complete_systemname[2:]+jobname+'.py'
    jobfilename = complete_systemname[2:]+"_"+jobname
    with open(scriptfilename, 'w') as scriptf:
        print(
            'import os, sys'
            '\nfrom bilana2 import Systeminfo'
            '\nfrom bilana2 import order'
            '\nneighbor_map = bl.neighbor.get_neighbor_dict(neighborfilename="{1}")'
            '\nsysinfo = Systeminfo(inputfilepath="{0}")'
            '\norder.calc_tilt(sysinfo)'
            '\norder.create_cc_orderfiles(sysinfo, neighbor_map)'
            '\nos.remove(sys.argv[0])'.format(inputfilename, neighborfile),
            file=scriptf)
        if not dry:
            write_submitfile('submit.sh', jobfilename, mem='12G', ncores=8, prio=False)
            cmd = ['sbatch', '-J', jobfilename, 'submit.sh','python3', scriptfilename]
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = proc.communicate()
            print(out.decode(), err.decode())

def check_and_write(systemname, temperature, jobname, lipidpart, *args,
                    overwrite=True,
                    neighborfilename="neighbor_info",
                    inputfilename="inputfile",
                    energyfilename="all_energies.dat",
                    scdfilename="scd_distribution.dat",
                    dry=False,
                    **kwargs,):
    ''' Check if all energy files exist and write table with all energies '''
    complete_systemname = './{}_{}'.format(systemname, temperature)
    os.chdir(complete_systemname)
    scriptfilename = 'exec'+complete_systemname[2:]+jobname+'.py'
    jobfilename = complete_systemname[2:]+"_"+jobname
    if overwrite:
        oflag = "--overwrite"
    else:
        oflag = ""
    with open(scriptfilename, 'w') as scriptf:
        print(
            '\nimport os, sys'
            '\nimport bilana2 as bl'
            '\nfrom bilana2 import Energy'
            '\nneighbor_map = bl.neighbor.get_neighbor_dict(neighborfilename="{3}")'
            '\nenergy_instance = Energy("{0}", neighbor_map, overwrite={1}, inputfilenpath="{2}")'
            '\nif bl.energy.check_exist_xvgs(energy_instance, check_len=energy_instance.universe.trajectory[-1].time):'
            '\n    bl.energy.write_energyfile(energy_instance)'
            '\n    bl.files.create_eofs(efile="{4}", sfile="{5}")'.format(lipidpart, overwrite,
                inputfilename, neighborfilename, energyfilename, scdfilename),
            file=scriptf)
        if not dry:
            write_submitfile('submit.sh', jobfilename, mem='16G')
            cmd = ['sbatch', '-J', jobfilename, 'submit.sh','python3', scriptfilename]
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = proc.communicate()
            print(out.decode(), err.decode())

def write_selfinteraction(systemname, temperature, jobname, lipidpart, *args,
    inputfilename="inputfile",
    neighborfilename="neighbor_info",
    dry=False,
    **kwargs,):
    ''' Write selfinteractions.dat from existing .edr files '''
    complete_systemname = './{}_{}'.format(systemname, temperature)
    os.chdir(complete_systemname)
    scriptfilename = 'exec'+complete_systemname[2:]+jobname+'.py'
    jobfilename = complete_systemname[2:]+"_"+jobname
    with open(scriptfilename, 'w') as scriptf:
        print(\
            'import os, sys'
            '\nfrom bilana.analysis.energy import Energy'
            '\nenergy_instance = Energy("{0}", inputfilepath="{1}", neighborfilename="{2}")'
            '\nenergy_instance.selfinteractions_edr_to_xvg()'
            '\nenergy.selfinteractions_xvg_to_dat(energy_instance)'
            '\nos.remove(sys.argv[0])'.format(lipidpart, inputfilename, neighborfilename),
            file=scriptf)
        if not dry:
            write_submitfile('submit.sh', jobfilename, mem='16G', prio=True)
            cmd = ['sbatch', '-J', jobfilename, 'submit.sh','python3', scriptfilename]
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = proc.communicate()
            print(out.decode(), err.decode())

#def write_eofscd(systemname, temperature, jobname, lipidpart, *args,
#    inputfilename="inputfile",
#    neighborfilename="neighbor_info",
#    energyfilename="all_energies.dat",
#    scdfilename="scd_distribution.dat",
#    dry=False,
#    **kwargs,):
#    ''' Write eofscd file from table containing all interaction energies '''
#    complete_systemname = './{}_{}'.format(systemname, temperature)
#    os.chdir(complete_systemname)
#    scriptfilename = 'exec'+complete_systemname[2:]+"_"+jobname+'.py'
#    jobfilename = complete_systemname[2:]+jobname
#    with open(scriptfilename, 'w') as scriptf:
#        print(\
#            'import os, sys'
#            '\nfrom bilana.analysis.energy import Energy'
#            '\nfrom bilana.files.eofs import EofScd'
#            '\nenergy_instance = Energy("{0}", inputfilename="{1}", neighborfilename="{2}")'
#            '\nif energy_instance.check_exist_xvgs(check_len=energy_instance.t_end):'
#            '\n    eofs = EofScd("{0}", inputfilename="{1}", energyfilename="{4}", scdfilename="{3}")'
#            '\n    eofs.create_eofscdfile()'
#            '\nelse:'
#            '\n    raise ValueError("There are .edr files missing.")'
#            '\nos.remove(sys.argv[0])'.format(lipidpart, inputfilename, neighborfilename,  scdfilename, energyfilename),
#            file=scriptf)
#        if not dry:
#            write_submitfile('submit.sh', jobfilename, mem='16G', prio=True)
#            cmd = ['sbatch', '-J', jobfilename, 'submit.sh','python3', scriptfilename]
#            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#            out, err = proc.communicate()
#            print(out.decode(), err.decode())

#def write_nofscd(systemname, temperature, jobname, *args,
#    inputfilename="inputfile",
#    neighborfilename="neighbor_info",
#    scdfilename="scd_distribution.dat",
#    dry=False,
#    **kwargs,):
#    ''' Write nofscd file from files containing the order parameter distribution and the neighbor mapping of the system '''
#    complete_systemname = './{}_{}'.format(systemname, temperature)
#    os.chdir(complete_systemname)
#    scriptfilename = 'exec'+complete_systemname[2:]+jobname+'.py'
#    jobfilename = complete_systemname[2:]+"_"+jobname
#    with open(scriptfilename, 'w') as scriptf:
#        print(\
#            '\nimport os, sys'
#            '\nfrom bilana.files.nofs import NofScd'
#            '\nnofs = NofScd(inputfilename="{}")'
#            '\nnofs.create_NofScd_input(scdfilename="{}", neighborfilename="{}")'
#            '\nos.remove(sys.argv[0])'.format(inputfilename, scdfilename, neighborfilename),
#            file=scriptf)
#        if not dry:
#            write_submitfile('submit.sh', jobfilename, mem='8G', prio=True)
#            cmd = ['sbatch', '-J', jobfilename, 'submit.sh','python3', scriptfilename]
#            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#            out, err = proc.communicate()
#            print(out.decode(), err.decode())
