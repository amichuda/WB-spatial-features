
import yaml
import sys

def clean_conda_env_export(input_file, output_file, platform_packages_to_remove):
    with open(input_file, 'r') as f:
        # It's better to process line by line for conda export format which combines yaml and pip
        lines = f.readlines()

    clean_lines = []
    
    # Simple state machine to parsing
    in_pip = False
    
    for line in lines:
        stripped = line.strip()
        if stripped == "dependencies:":
            clean_lines.append(line)
            continue
        if stripped.startswith("- pip:"):
            clean_lines.append(line)
            in_pip = True
            continue
        if stripped.startswith("prefix:"):
            continue
        if not stripped.startswith("-"):
            clean_lines.append(line)
            continue

        # Processing dependencies
        if in_pip:
            # pip packages: usually package==version
            # just keep them as is
            clean_lines.append(line)
        else:
            # conda packages: package=version=build or package=version
            # or package
            parts = stripped.split('=')
            pkg_name = parts[0][2:] # Remove "- "
            
            if pkg_name in platform_packages_to_remove:
                continue
                
            # Keep only package name and maybe version if it's not a build string
            # Heuristic: keep package=version, drop build
            if len(parts) >= 2:
                new_line = f"  - {parts[0][2:]}={parts[1]}\n"
                clean_lines.append(new_line)
            else:
                clean_lines.append(line)

    with open(output_file, 'w') as f:
        f.writelines(clean_lines)
    print(f"Created {output_file}")

# Linux specific packages to remove
linux_pkgs = [
    "_libgcc_mutex",
    "_openmp_mutex",
    "ld_impl_linux-64",
    "libgcc-ng",
    "libgomp",
    "libstdcxx-ng",
    "libnsl",
    "libuuid",  # can cause issues on mac
    "libxcrypt", # often linux specific
    "__linux"
]

clean_conda_env_export('gee_env.yaml', 'gee_env_clean.yaml', linux_pkgs)

# Also create spfeas_env_clean.yml if it exists
try:
    clean_conda_env_export('spfeas_env.yml', 'spfeas_env_clean.yml', linux_pkgs)
except FileNotFoundError:
    print("spfeas_env.yml not found")

