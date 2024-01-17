#!/bin/bash

cd ~/
python3 ~/soccer_api/src/statistics_aggregation.py data_extraction.first_run=False && echo Aggregations are updated!