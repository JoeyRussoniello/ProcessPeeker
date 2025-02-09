"""
ProcessPeeker: A script to monitor process performance using psutil.
"""

import psutil
import time
from datetime import datetime
import csv
import os
import argparse
import logging
from concurrent.futures import ThreadPoolExecutor
from queue import Queue

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

stop_monitoring = False
queue = Queue()

def get_run_number():
    """
    Get the run number for the current execution.
    If the CSV file does not exist, return 1.
    Otherwise, return the next iteration number based on the last entry in the CSV file.
    """
    if not os.path.isfile('process_info.csv'):
        return 1
    with open('process_info.csv', mode='r') as f:
        for line in f:
            pass
        last_line = line
        last_val = last_line.split(',')[0]
        return int(last_val) + 1 if last_val != 'Iter' else 1

def get_process_names():
    """
    Prompt the user to enter the names of the processes to track.
    Returns a list of process names.
    """
    vals = input("Enter the names of the processes to track (comma separated, e.g: duckduckgo,chrome): ").lower().split(',')
    return [val.strip() for val in vals]

def get_process_id(process):
    """
    Get the process ID for a given process name.
    Returns the process ID if found, otherwise returns None.
    """
    for proc in psutil.process_iter(['pid', 'name']):
        process_info = proc.info
        if process in process_info['name'].lower():
            logging.info(f"PID: {process_info['pid']}, Name: {process_info['name']}")
            return process_info['pid']
    logging.info("Process ID Not Found")
    return None

def get_process_info(process:psutil.Process, interval):
    """
    Get the performance information for a given process.
    Returns a dictionary with process information.
    """
    with process.oneshot():
        name = process.name()
        cpu_usage = process.cpu_percent(interval=interval)
        memory_info = process.memory_percent(memtype='rss',interval=interval)
        disk_io = process.io_counters(interval=interval)
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return {
            'time': current_time,
            'process': name,
            'cpu_usage': cpu_usage,
            'memory_usage': memory_info,
            'disk_read_count': disk_io.read_count,
            'disk_write_count': disk_io.write_count,
            'disk_read_bytes': disk_io.read_bytes,
            'disk_write_bytes': disk_io.write_bytes
        }

def monitor_process(process_name, runnumber, interval):
    """
    Monitor the performance of a given process.
    Collects process information at specified intervals and puts it into a queue.
    """
    global stop_monitoring
    pid = get_process_id(process_name)
    process = psutil.Process(pid)
    while not stop_monitoring:
        process_info = get_process_info(process, interval)
        if process_info:
            queue.put([
                runnumber,
                process_info['time'],
                process_info['process'],
                process_info['cpu_usage'],
                process_info['memory_usage'],
                process_info['disk_read_count'],
                process_info['disk_write_count'],
                process_info['disk_read_bytes'],
                process_info['disk_write_bytes']
            ])
            logging.info(process_info)
        else:
            logging.info(f"Process with PID {pid} not found. Trying to find new PID.")
            pid = get_process_id(process_name)
        time.sleep(interval)

def listen_for_exit():
    """
    Listen for user input to stop the monitoring process.
    Sets the stop_monitoring flag to True when 'exit' or 'e' is entered.
    """
    global stop_monitoring
    while True:
        user_input = input().strip().lower()
        if user_input == 'exit' or user_input == 'e':
            stop_monitoring = True
            logging.info("Input heard. Waiting for all threads to finish/write outputs to csv.")
            break

def write_to_csv():
    """
    Write the collected process information to a CSV file.
    Continues writing until monitoring is stopped and the queue is empty.
    """
    file_exists = os.path.isfile('process_info.csv')
    with open('process_info.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(['Iter', 'Time', 'Process', 'CPU Usage', 'Memory Usage', 'Disk Read Count', 'Disk Write Count', 'Disk Read Bytes', 'Disk Write Bytes'])
        while not stop_monitoring or not queue.empty():
            while not queue.empty():
                writer.writerow(queue.get())

def main():
    """
    Main function to parse arguments, get process names, and start monitoring.
    """
    parser = argparse.ArgumentParser(description="Process Monitoring Script")
    parser.add_argument('-i', '--interval', type=float, default=5, help='Interval between each survey in seconds')
    args = parser.parse_args()

    runnumber = get_run_number()
    process_names = get_process_names()

    logging.info(f"Monitoring started with Iter-id {runnumber}. Type 'exit' to stop.")

    with ThreadPoolExecutor(max_workers=len(process_names) + 2) as executor:
        for process_name in process_names:
            executor.submit(monitor_process, process_name.strip(), runnumber, args.interval)
        executor.submit(listen_for_exit)
        executor.submit(write_to_csv)

main()