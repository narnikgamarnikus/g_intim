#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset


celery -A g_intim.taskapp beat -l INFO
