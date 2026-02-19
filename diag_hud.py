
import sys
import subprocess
import os

def run_diagnostics():
    print("Starting HUD Diagnostics...")
    env = os.environ.copy()
    # Forces standard output to be unbuffered
    env["PYTHONUNBUFFERED"] = "1"
    
    try:
        # Run hud_main.py and capture both stdout and stderr
        process = subprocess.Popen(
            [sys.executable, "hud_main.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            env=env
        )
        
        # Read output in real-time for up to 60 seconds
        timeout = 60
        start_time = os.times().elapsed
        
        output_log = []
        import time
        start_ts = time.time()
        
        while time.time() - start_ts < timeout:
            line = process.stdout.readline()
            if not line:
                if process.poll() is not None:
                    break
                continue
            
            print(f"[HUD] {line.strip()}")
            output_log.append(line)
        
        if process.poll() is None:
            print("HUD is still running after timeout. Terminating...")
            process.terminate()
        else:
            print(f"HUD exited with code: {process.returncode}")
            
        with open("diag_hud_output.txt", "w", encoding="utf-8") as f:
            f.writelines(output_log)
            
    except Exception as e:
        print(f"Diagnostics Error: {e}")

if __name__ == "__main__":
    run_diagnostics()
