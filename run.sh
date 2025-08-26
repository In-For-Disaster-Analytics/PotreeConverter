#!/bin/bash

OUTPUTS_DIR=${_tapisExecSystemOutputDir}

potreeconverter -i ${converterInput} -o ${OUTPUTS_DIR}
echo ${_tapisDtnSystemOutputDir}
echo ${_tapisDtnSystemInputDir}
