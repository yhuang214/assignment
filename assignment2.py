#!/usr/bin/env python3

import argparse

import os, sys

def parse_command_args() -> object:

  "Set up argparse here. Call this function inside main."

  parser = argparse.ArgumentParser(description="Memory Visualiser -- See Memory Usage Report with bar charts",epilog="Copyright 2023")

  parser.add_argument("-l", "--length", type=int, default=20, help="Specify the length of the graph. Default is 20.")

  # Make this entry for human-readable. Check the docs to make it a True/False option.

  parser.add_argument("-H", "--human-readable", action="store_true", help="Prints sizes in human readable format")

  parser.add_argument("program", type=str, nargs='?', help="if a program is specified, show memory use of all associated processes. Show only total use if not.")

  args = parser.   parse_args()

  return args

def percent_to_graph(percent: float, length: int=20) -> str:

  "turns a percent 0.0 - 1.0 into a bar graph"

  num_hashes = int(percent * length)
  num_spaces = length - num_hashes
  return '#' * num_hashes + ' ' * num_spaces

def get_sys_mem() -> int:

  "return total system memory (used or available) in kB"

  # open the meminfo file to accomplish the task!

  f = open("/proc/meminfo", "r") 
  for line in f:
      if line[:8] == "MemTotal": 
          total_mem = int(line.split()[1])
          f.close()  
          return total_mem
  f.close() 
  return 0


def get_avail_mem() -> int:

  "return total memory that is currently in use"

  # open the meminfo file to accomplish the task!

  f = open("/proc/meminfo", "r")  
  for line in f:
      if line[:13] == "MemAvailable": 
          avail_mem = int(line.split()[1])
          f.close()  
          return avail_mem
  f.close() 
  return 0

def pids_of_prog(app_name: str) -> list:
    "given an app name, return all pids associated with app"
     
    # please use os.popen('pidof <app>') to accomplish the task!

    command = 'pidof ' + app_name  
    pids = os.popen(command).read().strip()
    
    if pids:
        return pids.split()
    else:
        return []


def rss_mem_of_pid(proc_id: str) -> int:
    "given a process id, return the Resident memory used"
    
    # for a process, open the smaps file and return the total of each

  # Rss line.

    rss_total = 0
    smaps_file = "/proc/" + proc_id + "/smaps"
    try:
        f = open(smaps_file, "r")
        for line in f:
            if line[:4] == "Rss:":
                rss_total += int(line.split()[1])
        f.close()
    except FileNotFoundError:
        pass  
    return rss_total



def bytes_to_human_r(kibibytes: int, decimal_places: int=2) -> str:

  "turn 1,024 into 1 MiB, for example"

  suffixes = ['KiB', 'MiB', 'GiB', 'TiB', 'PiB'] # iB indicates 1024

  suf_count = 0

  result = kibibytes 

  while result > 1024 and suf_count < len(suffixes):

    result /= 1024

    suf_count += 1

  str_result = f'{result:.{decimal_places}f} '

  str_result += suffixes[suf_count]

  return str_result

if __name__ == "__main__":
    args = parse_command_args()

    total_mem = get_sys_mem()

    
    program_specified = False
    if args.program:
        if len(args.program) > 0:
            program_specified = True

    if program_specified:  
        pids = pids_of_prog(args.program)
        total_rss = 0

        for pid in pids:
            rss = rss_mem_of_pid(pid)
            percent_used = rss / total_mem
            graph = percent_to_graph(percent_used, args.length)

            if args.human_readable:
                rss_human = bytes_to_human_r(rss)
                print(pid + " [" + graph + " | " + str(int(percent_used * 100)) + "%] " + rss_human + "/" + bytes_to_human_r(total_mem))
            else:
                print(pid + " [" + graph + " | " + str(int(percent_used * 100)) + "%] " + str(rss) + "/" + str(total_mem))

            total_rss += rss

        
        percent_total_used = total_rss / total_mem
        total_graph = percent_to_graph(percent_total_used, args.length)

        if args.human_readable:
            total_rss_human = bytes_to_human_r(total_rss)
            print(args.program + " [" + total_graph + " | " + str(int(percent_total_used * 100)) + "%] " + total_rss_human + "/" + bytes_to_human_r(total_mem))
        else:
            print(args.program + " [" + total_graph + " | " + str(int(percent_total_used * 100)) + "%] " + str(total_rss) + "/" + str(total_mem))

    else:  
        avail_mem = get_avail_mem()
        used_mem = total_mem - avail_mem
        percent_used = used_mem / total_mem
        graph = percent_to_graph(percent_used, args.length)

        if args.human_readable:
            used_mem_human = bytes_to_human_r(used_mem)
            total_mem_human = bytes_to_human_r(total_mem)
            print("Memory         [" + graph + " | " + str(int(percent_used * 100)) + "%] " + used_mem_human + "/" + total_mem_human)
        else:
            print("Memory         [" + graph + " | " + str(int(percent_used * 100)) + "%] " + str(used_mem) + "/" + str(total_mem))
