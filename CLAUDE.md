# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PotreeConverter v2.0 is a C++ application that generates octree LOD structures for streaming and real-time rendering of massive point clouds. It converts LAS/LAZ files into a format viewable in web browsers with Potree or PotreeDesktop. Version 2.0 is 10-50x faster than v1.7 and produces only 3 files instead of thousands.

## Build Commands

### Native Build (Linux/macOS/Windows)

```bash
mkdir build
cd build
cmake ../
make        # Linux/macOS
# Or open Visual Studio 2019 Project ./Converter/Converter.sln on Windows
```

### Docker Build (Recommended)

```bash
# Build locally
docker build -t potreeconverter .

# Or pull pre-built image
docker pull ghcr.io/in-for-disaster-analytics/potreeconverter:latest
```

## Usage Commands

### Docker Usage

```bash
# Basic conversion
docker run -it --user $(id -u):$(id -g) \
  -v /path/to/input:/data \
  potreeconverter -i /data/input.laz -o /data/output

# With sampling strategy
docker run -it --user $(id -u):$(id -g) \
  -v /path/to/input:/data \
  potreeconverter -i /data/input.laz -o /data/output -m poisson
```

### TACC/Apptainer Usage

```bash
module load tacc-apptainer
apptainer exec docker://ghcr.io/in-for-disaster-analytics/potreeconverter:latest \
  PotreeConverter -i /path/to/input.laz -o /path/to/output -m poisson
```

### Native Binary Usage

```bash
PotreeConverter <input> -o <outputDir> -m <sampling_method>
# Sampling methods: poisson (default), random
```

## Architecture

### Core Components

- **Main Application**: `Converter/src/main.cpp` - Entry point and CLI handling
- **Chunker**: `chunker_countsort_laszip.cpp/.h` - Point cloud chunking with LAZ compression
- **Indexer**: `indexer.cpp/.h` - Octree index generation and spatial organization
- **LasLoader**: `modules/LasLoader/` - LAS/LAZ file parsing and loading
- **Utilities**: `converter_utils.h`, `logger.cpp/.h`, `structures.h`

### Dependencies

- **LASlip**: `libs/laszip/` - LAZ compression/decompression
- **Brotli**: `libs/brotli/` - General compression library
- **JSON**: `libs/json/` - Single-header JSON library
- **TBB**: Intel Threading Building Blocks (system dependency)
- **Arguments**: `libs/arguments/` - Command-line argument parsing

### Output Structure

The converter produces 3 files:

1. `metadata.json` - Point cloud metadata and structure
2. Octree hierarchy file
3. Point data file

### Sampling Strategies

- **Poisson-disk sampling** (default): Even distribution, better quality
- **Random sampling**: Faster but less uniform distribution

## Testing

The project includes test utilities:

- `tools/testing.mjs` - Node.js testing script for Windows
- `testing/testing.mjs` - Cross-platform testing utilities
- Test data located in `scripts/test_data/`

## Python Integration

The `scripts/potree_scene_generator.py` provides Python utilities for scene generation and metadata handling. Uses only Python standard library (no external dependencies).

## TACC Configuration

The `app.json` file configures the application for TACC systems with Tapis integration. The `run.sh` script handles TACC execution workflow with proper input/output directory handling.
