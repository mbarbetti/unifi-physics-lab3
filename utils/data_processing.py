import os
import numpy as np
import pandas as pd


def data_processing ( files_path : str ,
                      export_dir : str ,
                      tdc_resolution : float = 1e-9 ) -> pd.DataFrame:
  group_names = os.listdir (files_path)

  info = list()   # manipulation data container

  for g in group_names:

    num_files = len( os.listdir (f"{files_path}/{g}") )

    ##   Single data file
    ## --------------------
    if num_files == 2:

      if os.path.exists ( f"{files_path}/{g}/Dati_{g}.txt" ):
        file_name = f"{files_path}/{g}/Dati_{g}"
      else:
        file_name = f"{files_path}/{g}/Dati"

      with open ( f"{file_name}.txt", "r" ) as f:
        lines = f.readlines()

      tot_time = float(lines[3].split(" ")[-1][:-1])
      tot_events = int(lines[4].split(" ")[-1][:-1])

      data = pd.read_csv ( f"{file_name}.txt", header = 4, delim_whitespace = True )
      data = data . drop ( ["Time", "Valido"], axis = 1 )
    
    ##   Multiple data file
    ## ----------------------
    else:

      tot_time = 0.0
      tot_events = 0
      data = list()

      if os.path.exists ( f"{files_path}/{g}/Dati_{g}.txt" ):
        file_name = f"{files_path}/{g}/Dati_{g}"
      elif os.path.exists ( f"{files_path}/{g}/Dati_{g}_1.txt" ):
        file_name = f"{files_path}/{g}/Dati_{g}_1"
      else:
        file_name = f"{files_path}/{g}/Dati"

      with open ( f"{file_name}.txt", "r" ) as f:
        lines = f.readlines()
      
      tot_time += float(lines[3].split(" ")[-1][:-1])
      tot_events += int(lines[4].split(" ")[-1][:-1])
      data . append ( pd.read_csv ( f"{file_name}.txt", header = 4, delim_whitespace = True ) )

      for i in range(2, num_files - 1):

        with open ( f"{file_name}_{i}.txt", "r") as f:
          other_lines = f.readlines()
        
        tot_time += float(other_lines[3].split(" ")[-1][:-1])
        tot_events += int(other_lines[4].split(" ")[-1][:-1])
        data . append ( pd.read_csv ( f"{file_name}_{i}.txt", header = 4, delim_whitespace = True ) )

      data = pd.concat ( data, axis = 0, ignore_index = True )
      data = data . drop ( ["Time", "Valido"], axis = 1 )

    ## Data processing
    noise = np.random.normal ( 0.0, tdc_resolution, size = len(data) )
    theta_0 = np.random.uniform ( -1e-7, 1e7 )
    theta_1 = np.random.uniform ( -0.2, 0.2 ) + 1.0

    info . append ( [g, tdc_resolution, theta_0, theta_1] )

    ## New values for TDC
    data["TDC"] = theta_1 * data["TDC"] + theta_0 + noise

    ## Export step
    data.to_csv ( f"{export_dir}/data_{g}.txt", header = data.columns, index = None, sep = " " )

    with open ( f"{export_dir}/data_{g}.txt", "r" ) as f:
      only_data = f.readlines()
    
    lines[3] = "{}: {}\n" . format ( lines[3].split(":")[0], tot_time )
    lines[4] = "{}: {}\n" . format ( lines[4].split(":")[0], tot_events )

    with open ( f"{export_dir}/data_{g}.txt", "w" ) as f:
      f.writelines ( lines[:6] + only_data )

  return pd.DataFrame ( info, columns = ["Group", "TDC resolution", "theta_0", "theta_1"] )
