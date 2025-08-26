#!/bin/bash

OUTPUTS_DIR=${_tapisExecSystemOutputDir}
WEB_SERVER_DIR=/corral/utexas/BCS24011/ckan/lidar_files

potreeconverter -i ${converterInput} -o ${OUTPUTS_DIR}

PARENT_POINT_CLOUD_DIR=${WEB_SERVER_DIR}/${_tapisJobCreateDate}
POINT_CLOUD_DIR=${PARENT_POINT_CLOUD_DIR}/${_tapisJobName}-${_tapisJobUuid}
mkdir -p ${POINT_CLOUD_DIR}
cp -r ${OUTPUTS_DIR} ${POINT_CLOUD_DIR}
setfacl -R -m u:33:rx ${PARENT_POINT_CLOUD_DIR}
