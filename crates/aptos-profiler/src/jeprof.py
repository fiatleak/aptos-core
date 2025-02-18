import subprocess
import sys

def execute_command(command):
    try:
        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        return output.decode('utf-8').strip()
    except subprocess.CalledProcessError as e:
        return f"Command execution failed with error code {e.returncode}. Output:\n{e.output.decode('utf-8').strip()}"

text_location = sys.argv[1]
svg_location = sys.argv[2]


command = "jeprof --show_bytes ./target/release/aptos-node ./*.heap --svg  > " + svg_location
result = execute_command(command)
command = "jeprof --show_bytes ./target/release/aptos-node ./*.heap --text  > " + text_location
result = execute_command(command)

command = "rm ./*.heap"
result = execute_command(command)
