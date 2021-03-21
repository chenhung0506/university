#!/bin/bash
PUSH_IMG='false'
# GIT_HEAD=$(git rev-parse --short=7 HEAD)
# GIT_DATE=$(git log HEAD -n1 --pretty='format:%cd' --date=format:'%Y%m%d-%H%M')
# GIT_DATE=$(date '+%Y%m%d-%H%M') 
# TAG=$GIT_HEAD-$GIT_DATE

WORK_PATH=$(dirname "$0")
source ${WORK_PATH}/build.sh 

ENV=dev.env
export TAG='latest'
export REPO=harbor.chlin.tk/python
export CONTAINER=university

getopts_help $@
select_number $1
echo "mode: "$?

if [[ "$1" =~ ^[0-9] ]]
    then
    echo "befor:" $@
    set -- "${@:2:$#}"
    echo "after:" $@
fi

setting_getopts $@
execute_option $mode

if [ $PUSH_IMG = 'true' ] ; then
    execute_option 5
fi