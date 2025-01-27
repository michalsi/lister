import os
import sys
import subprocess

def run_pytest():
    # Get the current Python executable
    python_executable = sys.executable

    # Construct the command to run pytest through uv
    command = [python_executable, "-m", "pytest"] + sys.argv[1:]

    # Set up the environment
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"  # Ensures Python output is not buffered

    try:
        # Run the command
        process = subprocess.Popen(
            command,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )

        # Print output in real-time
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())

        # Print any errors
        stderr_output = process.stderr.read()
        if stderr_output:
            print("Errors:", file=sys.stderr)
            print(stderr_output, file=sys.stderr)

        # Check the return code
        if process.returncode != 0:
            print(f"pytest exited with return code {process.returncode}", file=sys.stderr)
            sys.exit(process.returncode)

    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    run_pytest()