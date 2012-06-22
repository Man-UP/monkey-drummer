#!/bin/bash

set -o errexit
set -o nounset

readonly REPO="$(readlink -f -- "$(dirname -- "${0}")/..")"
cd -- "${REPO}"

echo
echo !!! START HYDROGEN !!!
echo

(
    inotifywait /tmp/output.mid
    aplaymidi --port 14:0 /tmp/output.mid &> /dev/null &
) &> /dev/null &

./scripts/run.sh -g /tmp/graph.png -o /tmp/output.mid -r 5 \
        $(find test test/files.ifnimidi.com/ -name '*.mid' | shuf -n 5)

eog --fullscreen /tmp/graph.png &> /dev/null &

echo 'Waiting for aplaymidi...'
wait

