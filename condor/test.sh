#!/bin/bash

PTWGT=${1}

echo ">> $PTWGT"
if [ $PTWGT == "NONE" ]; then
    echo "   .. running without pt re-weighting"
else
    echo "   .. running with pt re-weighting"
fi
