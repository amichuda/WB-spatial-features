# World Bank Spatial Features Extraction for Malawi

## Description
This replication package contains a set of Python scripts and configuration files designed to extract spatial features from Sentinel-2 imagery for the Malawi study area. The workflow includes downloading imagery from Google Earth Engine (GEE), processing it to handle missing values, creating mosaics, and extracting both spatial (using `spfeas`) and time-series features. This project supports research activities, likely related to World Bank initiatives, by providing processed geospatial variables.

## Installation Instructions

This project requires multiple Conda environments due to conflicting dependency requirements (e.g., Python 3.6 for `spfeas` vs Python 3.12 for GEE).

### Prerequisites
- [Anaconda](https://www.anaconda.com/products/distribution) or [Miniforge](https://github.com/conda-forge/miniforge) installed.
- Google Earth Engine account and project enabled.

### Setting up Environments

1.  **GEE Environment (`gee`)**:
    Used for downloading imagery.
    ```bash
    # Note: On macOS ARM64 (Apple Silicon), you may need to use the cleaned version provided in the repo if the original fails.
    # We have created 'gee_env_clean.yaml' for this purpose.
    conda env create -f gee_env_clean.yaml
    ```

2.  **Spfeas Environment (`spfeas`)**:
    Used for spatial feature extraction (requires Python 3.6 and GDAL 2).
    *Warning: This environment relies on legacy packages unavailable for macOS ARM64 (M1/M2/M3). It may only work on Intel-based Linux/macOS systems.*
    ```bash
    # You can use the provided script
    chmod +x install_reqs.sh
    ./install_reqs.sh
    
    # Or manually utilizing spfeas_env.yml if preferred, but install_reqs.sh is recommended for specific pip packages.
    ```

3.  **Geowombat / Xr_fresh Environment (`geowombat`)**:
    Used for image processing and time series features.
    ```bash
    # Create the environment using the provided yaml
    conda env create -f geowombat_env.yaml
    ```

## Usage Guidelines

The pipeline is designed to be run sequentially. A `main.py` script is provided to help orchestrate these steps, but due to different environment requirements, you may need to run steps individually or ensure `conda run` is configured correctly.

**Important**: Before running Step 1, you must authenticate with Google Earth Engine:
```bash
conda activate gee
earthengine authenticate
```

### Running with main.py
The `main.py` script attempts to run the workflow using `conda run` to switch environments.

```bash
python main.py
```

### Manual Execution Steps

1.  **Download Imagery**:
    ```bash
    conda activate gee
    earthengine authenticate # Run once if not authenticated
    python 0_gee_download.py
    ```

2.  **Interpolate Missing Values**:
    ```bash
    conda activate geowombat # or xr_fresh
    python 1_interpolate_missing_values.py
    ```

3.  **Create Mosaics**:
    ```bash
    conda activate geowombat
    python 2_create_mosaics.py
    ```

4.  **Run Spfeas**:
    ```bash
    conda activate spfeas
    python 3_run_spfeas.py
    ```

5.  **Convert Features to TIFs**:
    ```bash
    conda activate spfeas
    python 4_features_to_tifs.py
    ```

6.  **Organize TIFs**:
    ```bash
    conda activate geowombat
    python 5_organize_tifs.py
    # Or use the shell script for SLURM: sbatch 5a_organize_tifs.sh
    ```

7.  **Stack to Single Band (Optional)**:
    ```bash
    conda activate geowombat
    python 6_stack_2_single_band.py
    ```

8.  **Time Series Features**:
    ```bash
    conda activate xr_fresh
    python 7_time_series_features.py
    ```

## Explanation of Key Components

-   `0_gee_download.py`: Downloads Sentinel-2 quarterly composites (2021-2023) for Malawi using GEE Python API.
-   `1_interpolate_missing_values.py`: Fills missing data in the downloaded time series using `xr_fresh`.
-   `2_create_mosaics.py`: Mosaics the interpolated satellite imagery tiles into larger coverages (North/South).
-   `3_run_spfeas.py`: Wrapper to run the `spfeas` tool for calculating spatial contextual features (e.g., FOTO, Gabor, HOG).
-   `4_features_to_tifs.py`: Converts the raw VRT outputs from `spfeas` into GeoTIFF format.
-   `5_organize_tifs.py`: Sorts the generated feature TIFs into a structured directory hierarchy based on feature type and date.
-   `6_stack_2_single_band.py`: Helper to convert multiband mosaics into single-band files, often needed for specific time-series analysis tools.
-   `7_time_series_features.py`: Computes time-series metrics (e.g., mean, stability) from the image stacks.
-   `functions.py` & `helpers.py`: Contain utility functions used across the scripts.
-   `install_reqs.sh`: automated script to setup the legacy `spfeas` environment.

## Dependencies and Requirements

-   **Python**: Versions 3.6 (legacy) and 3.12+ (modern).
-   **Conda**: For environment management.
-   **Google Earth Engine**: For data access.
-   **Key Libraries**:
    -   `earthengine-api`
    -   `spfeas` (requires `gdal=2`, `opencv`)
    -   `geowombat`
    -   `xr_fresh`
    -   `gdal`
    -   `numpy`, `pandas`, `rasterio`

## Directory Overview

```
.
├── 0_gee_download.py           # Step 1: Download
├── 1_interpolate_missing_values.py # Step 2: Interpolate
├── 2_create_mosaics.py         # Step 3: Mosaic
├── 3_run_spfeas.py             # Step 4: Spatial Features
├── 4_features_to_tifs.py       # Step 5: Convert to TIF
├── 5_organize_tifs.py          # Step 6: Organize
├── 5a_organize_tifs.sh         # SLURM script for Step 6
├── 6_stack_2_single_band.py    # Step 7: Stack (Optional)
├── 7_time_series_features.py   # Step 8: Time Series Features
├── data/                       # Contains GeoJSON boundaries (north/south_adm2)
├── functions.py                # Shared functions
├── gee_env.yaml                # GEE Conda environment
├── helpers.py                  # Helper functions
├── install_reqs.sh             # Setup script for spfeas
├── requirements.txt            # Pip requirements for spfeas
└── spfeas_env.yml              # Base Conda env for spfeas
```

## Contact Information
For questions regarding this repository, please contact:
Michael Mann (mmann1123@gwu.edu)
