#!/bin/bash


INPUTS_DIR=${_tapisExecSystemInputDir}
OUTPUTS_DIR=${_tapisExecSystemOutputDir}

potreeconverter -i ${INPUTS_DIR}/ -o ${OUTPUTS_DIR}

# Find the metadata.json on ${OUTPUTS_DIR} as stored as variable
METADATA_FILE=$(find ${OUTPUTS_DIR} -name "metadata.json")

python scripts/potree_scene_generator.py ${METADATA_FILE} --output ${OUTPUTS_DIR} -u https://ckan.tacc.utexas.edu/lidar_files/