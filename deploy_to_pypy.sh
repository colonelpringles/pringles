#!/bin/bash

ENV=$1
CURRENT_VERSION=$(python setup.py --version)

function clean_previous_dist {
    yes | rm -rf dist/
}

function deploy_local {
    clean_previous_dist
    python setup.py sdist bdist_wheel
    WHEEL_FILENAME=$(ls dist|grep whl)
    pip install --ignore-installed dist/$WHEEL_FILENAME
}

echo "DEPLOYING pringles-v$CURRENT_VERSION"

if [[ "$ENV" == "LOCAL" ]]; then
    echo "LOCAL deployment"
    deploy_local
fi