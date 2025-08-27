#!/bin/bash
set -xe


OUTPUTS_DIR=${_tapisExecSystemOutputDir}
WEB_SERVER_DIR=/corral/utexas/BCS24011/ckan/lidar_files
WEB_SERVER_URL=https://ckan.tacc.utexas.edu/lidar_files

if [ -n "${sourcelas}" ]; then
	echo "Using value from env"
  /home/potree/PotreeConverter -i ${sourcelas} -o ${OUTPUTS_DIR}
else
	echo "Using default input"
	/home/potree/PotreeConverter -i ${_tapisExecSystemInputDir}/sourcelas -o ${OUTPUTS_DIR}
fi


# _tapisArchiveSystemDir: /corral/utexas/BCS24011/ckan/lidar_files/${JobCreateDate}/${JobName}-${JobUUID}


#PARENT_POINT_CLOUD_DIR=${WEB_SERVER_DIR}/${_tapisJobCreateDate}
#POINT_CLOUD_DIR=${PARENT_POINT_CLOUD_DIR}/${_tapisJobName}

# Copy the pointcloud on the webserver web-accessible
#mkdir -p ${POINT_CLOUD_DIR}
#cp -r ${OUTPUTS_DIR} ${POINT_CLOUD_DIR}

METADATA_FILE=${OUTPUTS_DIR}/metadata.json
METADATA_URL=${WEB_SERVER_URL}/${_tapisJobCreateDate}/${_tapisJobName}-${_tapisJobUUID}/metadata.json
SCENE_FILE=${OUTPUTS_DIR}/scene.json
SCENE_URL=${WEB_SERVER_URL}/${_tapisJobCreateDate}/${_tapisJobName}-${_tapisJobUUID}/scene.json

# Generate the scene file
python3 /tapis/potree_scene_generator.py \
	${METADATA_FILE} \
	--output-scene-file ${SCENE_FILE} \
	--base-url ${METADATA_URL}

#setfacl -R -m u:33:rx ${OUTPUTS_DIR}

echo "Scene URL: ${SCENE_URL}"