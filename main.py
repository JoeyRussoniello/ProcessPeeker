import psutil
import time
from datetime import datetime
import csv
import os
from concurrent.futures import ThreadPoolExecutor

stop_monitoring = False

def get_run_number():
    if not os.path.isfile('process_info.csv'):
        return 1
    with open('process_info.csv', mode='r') as f:
        for line in f:
            pass
        last_line = line
        last_val = last_line.split(',')[0]
        return int(last_val) + 1 if last_val != 'Iter' else 1
def get_process_names():
    vals = input("Enter the names of the processes to track (comma separated, e.g: duckduckgo,chrome): ").lower().split(',')
    return [val.strip() for val in vals]
def get_process_id(process):
    for proc in psutil.process_iter(['pid', 'name']):
        process_info = proc.info
        if process in process_info['name'].lower():
            print(f"PID: {process_info['pid']}, Name: {process_info['name']}")
            return process_info['pid']
    print("Process ID Not Found")
    return None

def get_process_info(pid):
    try:
        process = psutil.Process(pid)
        name = process.name()
        cpu_usage = process.cpu_percent(interval=1)
        memory_info = process.memory_info().rss
        disk_io = process.io_counters()
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
    except psutil.NoSuchProcess:
        return None

def monitor_process(process_name, runnumber, writer):
    global stop_monitoring
    pid = get_process_id(process_name)
    while not stop_monitoring:
        if pid:
            process_info = get_process_info(pid)
            if process_info:
                writer.writerow([
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
                print(process_info)
            else:
                print(f"Process with PID {pid} not found. Trying to find new PID.")
                pid = get_process_id(process_name)
        else:
            pid = get_process_id(process_name)
        time.sleep(10)

def listen_for_exit():
    global stop_monitoring
    while True:
        user_input = input().strip().lower()
        if user_input == 'exit' or user_input == 'e':
            stop_monitoring = True
            print("Monitoring stopped.")
            break

def main():
    runnumber = get_run_number()
    process_names = get_process_names()
    
    file_exists = os.path.isfile('process_info.csv')
    with open('process_info.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(['Iter', 'Time', 'Process', 'CPU Usage', 'Memory Usage', 'Disk Read Count', 'Disk Write Count', 'Disk Read Bytes', 'Disk Write Bytes'])

        print(f"Monitoring started with Iter-id {runnumber}. Type 'exit' to stop.")

        with ThreadPoolExecutor(max_workers=len(process_names) + 1) as executor:
            for process_name in process_names:
                executor.submit(monitor_process, process_name.strip(), runnumber, writer)
            executor.submit(listen_for_exit)

main()