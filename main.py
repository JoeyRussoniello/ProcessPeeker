import psutil
import time
from datetime import datetime
import csv
import threading
import os

stop_monitoring = False

def get_run_number():
    if not os.path.isfile('process_info.csv'):
        return 1
    with open('process_info.csv',mode='r') as f:
        for line in f:
            pass
        last_line = line
        last_val = last_line.split(',')[0]
        return int(last_val) + 1 if last_val != 'Iter' else 1
def get_process_id(process):
    """
    Get the process ID for a given process name.

    Args:
        process (str): The name of the process to find.

    Returns:
        int: The process ID if found, otherwise None.
    """
    for proc in psutil.process_iter(['pid', 'name']):
        process_info = proc.info
        if process in process_info['name'].lower():
            print(f"PID: {process_info['pid']}, Name: {process_info['name']}")
            return process_info['pid']
    print("Process ID Not Found")
    return None

def get_process_info(pid):
    """
    Get detailed information about a process.

    Args:
        pid (int): The process ID.

    Returns:
        dict: A dictionary containing process information.
    """
    try:
        process = psutil.Process(pid)
        name = process.name()
        cpu_usage = process.cpu_percent(interval=1)
        memory_info = process.memory_info().rss  # Get RSS memory usage
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

def monitor_process(process_name, runnumber,writer):
    """
    Monitor the process and write its information to a CSV file.

    Args:
        process_name (str): The name of the process to monitor.
        writer (csv.writer): The CSV writer object.
    """
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
    """
    Listen for user input to stop the monitoring process.
    """
    global stop_monitoring
    while True:
        user_input = input().strip().lower()
        if user_input == 'exit' or user_input == 'e':
            stop_monitoring = True
            print("Monitoring stopped.")
            break

def main():
    """
    Main function to start the monitoring process.
    """
    runnumber = get_run_number()
    process_name = input("Enter the name of the process to track (e.g: duckduckgo or chrome): ").strip().lower()
    
    file_exists = os.path.isfile('process_info.csv')
    with open('process_info.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(['Iter','Time', 'Process', 'CPU Usage', 'Memory Usage', 'Disk Read Count', 'Disk Write Count', 'Disk Read Bytes', 'Disk Write Bytes'])
        
        print("Monitoring started. Type 'exit' to stop.")
        
        # Start the monitoring thread
        monitor_thread = threading.Thread(target=monitor_process, args=(process_name, runnumber,writer))
        monitor_thread.start()
        
        # Start the input listening thread
        listen_thread = threading.Thread(target=listen_for_exit)
        listen_thread.start()
        
        # Wait for the threads to finish
        monitor_thread.join()
        listen_thread.join()

main()