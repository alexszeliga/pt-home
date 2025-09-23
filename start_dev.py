import subprocess
import sys

commands = [
    ['python', 'manage.py', 'runserver', '0.0.0.0:8000'],
    ['python', 'manage.py', 'tailwind', 'start']
]

processes = []

# Start each command in a separate process
for cmd in commands:
    processes.append(subprocess.Popen(cmd))

# Wait for all processes to finish (or handle termination)
try:
    for p in processes:
        p.wait()
except KeyboardInterrupt:
    print("Stopping processes...")
    for p in processes:
        p.terminate()
    sys.exit(0)