#!/bin/bash

SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"
PLUGDIR="${HOME}/.kicad_plugins"

if [ ! -d ${PLUGDIR} ]; then
    mkdir ${PLUGDIR}
fi

ln -s ${SCRIPTPATH}/edges2holes_action.py ${PLUGDIR}

