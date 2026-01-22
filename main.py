import os
import subprocess
import sys

# Instructions for the user:
# This script orchestrates the execution of the replication package.
# It assumes you have setting up the necessary Conda environments as described in the README.md.
# - 'gee': for GEE download (0_gee_download.py)
# - 'spfeas': for spatial features (3_run_spfeas.py, 4_features_to_tifs.py)
# - 'geowombat': or 'xr_fresh' for other processing steps.

def run_command(command, env_name=None):
    """
    Executes a shell command, optionally within a specific Conda environment.
    """
    if env_name:
        # Construct command to run within the conda environment
        # Note: This requires 'conda' to be in the PATH and initialized.
        cmd = f"conda run -n {env_name} {command}"
    else:
        cmd = command
    
    print(f"Executing: {cmd}")
    try:
        # use shell=True to allow complex commands; check=True to raise error on failure
        subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {cmd}")
        print(e)
        sys.exit(1)

def run_r_script(script_path, args=[]):
    """
    Executes an R script using rpy2 (if installed) or subprocess.
    """
    # Option 1: Using subprocess (simpler for running scripts)
    cmd = f"Rscript {script_path} {' '.join(args)}"
    run_command(cmd)

    # Option 2: Using rpy2 (as requested in instructions, logic provided as reference)
    try:
        import rpy2.robjects as robjects
        # This executes the R code in the current Python process
        with open(script_path, 'r') as f:
            r_code = f.read()
            robjects.r(r_code)
        print(f"Executed R script: {script_path} using rpy2")
    except ImportError:
        print("rpy2 not installed. Please install it to execute R code directly.")
    except Exception as e:
        print(f"Error executing R script with rpy2: {e}")

def run_stata_script(script_path):
    """
    Executes a Stata do-file using pystata.
    """
    try:
        import stata_setup
        stata_setup.config('/Applications/Stata/', 'mp') # Adjust path as needed
        from pystata import stata
        
        stata.run(script_path)
        print(f"Executed Stata script: {script_path}")
    except ImportError:
        print("pystata not installed or configured.")
    except Exception as e:
        print(f"Error executing Stata script: {e}")

def run_notebook(notebook_path, output_path=None, parameters=None):
    """
    Executes a Jupyter Notebook using papermill.
    """
    try:
        import papermill as pm
        if output_path is None:
            output_path = notebook_path # Overwrite or handle appropriately
        
        pm.execute_notebook(
            notebook_path,
            output_path,
            parameters=parameters
        )
        print(f"Executed notebook: {notebook_path}")
    except ImportError:
        print("papermill is not installed. Run: pip install papermill")
    except Exception as e:
        print(f"Error executing notebook: {e}")

def main():
    print("Starting Replication Package Workflow...")

    # Step 1: Download Imagery (Requires 'gee' environment)
    # Ensure you have run 'earthengine authenticate' previously
    print("\n--- Step 1: Downloading GEE Data ---")
    run_command("python 0_gee_download.py", env_name="gee")

    # Step 2: Interpolate Missing Values (Requires 'geowombat' or 'xr_fresh' environment)
    print("\n--- Step 2: Interpolating Missing Values ---")
    run_command("python 1_interpolate_missing_values.py", env_name="geowombat")

    # Step 3: Create Mosaics (Requires 'geowombat' environment)
    print("\n--- Step 3: Creating Mosaics ---")
    run_command("python 2_create_mosaics.py", env_name="geowombat")

    # Step 4: Run Spfeas (Requires 'spfeas' environment - Python 3.6)
    print("\n--- Step 4: Running Spfeas ---")
    run_command("python 3_run_spfeas.py", env_name="spfeas")

    # Step 5: Features to TIFs (Requires 'spfeas' environment)
    print("\n--- Step 5: Converting Features to TIFs ---")
    run_command("python 4_features_to_tifs.py", env_name="spfeas")

    # Step 6: Organize TIFs (Requires 'geowombat' environment)
    print("\n--- Step 6: Organizing TIFs ---")
    run_command("python 5_organize_tifs.py", env_name="geowombat")

    # Step 7: Stack to Single Band (Optional)
    print("\n--- Step 7: Stacking to Single Band (Optional) ---")
    run_command("python 6_stack_2_single_band.py", env_name="geowombat")

    # Step 8: Time Series Features (Requires 'xr_fresh' environment)
    print("\n--- Step 8: Extracting Time Series Features ---")
    run_command("python 7_time_series_features.py", env_name="xr_fresh")

    print("\nWorkflow completed successfully.")

    # --- Examples of running other file types (if they existed in the project) ---
    # run_r_script("analysis.R")
    # run_stata_script("model.do")
    # run_notebook("exploration.ipynb")

if __name__ == "__main__":
    main()
