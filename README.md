# ProcessPeeker

## Description
A basic Python script built on the `psutil` module to track major info about process performance.

## Installation and Dependencies
Download the ProcessPeeker repository by entering the following commands into git.
```git
git clone https://github.com/JoeyRussoniello/ProcessPeeker
cd ProcessPeeker
```

*Note: This program is dependent on the `psutil` module so the following command is needed to run:* 
```sh
pip install psutil
```

## Usage
Once downloaded, the `main.py` file can easily be called with:
```sh
python main.py
```
The script will prompt you to enter the names of the processes to track (comma separated, e.g: `duckduckgo,chrome`). The process will then stay running, examining process performance every specified interval (default is 5 seconds) until "exit" or "e" is pressed. Results will be saved into `process_info.csv`.

### Command Line Arguments
- `-i`, `--interval`: Interval between each survey in seconds (default is 5).

### Example
```sh
python main.py -i 10
```
This will monitor the specified processes every 10 seconds.

## Logging
The script uses logging to provide information about the monitoring process. Logs are printed to the console.

## Output CSV File Format
The output CSV file `process_info.csv` will have the following columns:
- Iter: Iteration number (ID # of script run, can be used to track data from individual script executions)
- Time: Timestamp of the data point
- Process: Name of the process
- CPU Usage: CPU usage percentage
- Memory Usage: Memory usage percentage
- Disk Read Count: Number of disk read operations
- Disk Write Count: Number of disk write operations
- Disk Read Bytes: Number of bytes read from disk
- Disk Write Bytes: Number of bytes written to disk

## Troubleshooting
### Common Issues
- **Process ID Not Found**: Ensure the process name is correct and running. If not found, will continue to iterate every `interval` until the process is started.
- **Permission Denied**: Run the script with appropriate permissions.
- **Module Not Found**: Ensure `psutil` is installed correctly using `pip install psutil`.

## Contribution
Contributions and feedback are welcome! Submit a pull request at any time!
