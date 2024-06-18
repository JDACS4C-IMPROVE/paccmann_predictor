
export JOBNAME=$parsl.localprovider.1717521480.68309
set -e
export CORES=$(getconf _NPROCESSORS_ONLN)
[[ "1" == "1" ]] && echo "Found cores : $CORES"
WORKERCOUNT=1
FAILONANY=0
PIDS=""

CMD() {
process_worker_pool.py --debug  -a 130.202.148.217,clswl217.cels.anl.gov -p 0 -c 1 -m None --poll 10 --task_port=54927 --result_port=54913 --logdir=/Users/priyanka/Documents/Argonne/Model_Curation/IMPROVE/improve/CSA/runinfo/088/"hpo_local" --block_id=0 --hb_period=30  --hb_threshold=120 --cpu-affinity none --available-accelerators  --start-method fork
}
for COUNT in $(seq 1 1 $WORKERCOUNT); do
    [[ "1" == "1" ]] && echo "Launching worker: $COUNT"
    CMD $COUNT &
    PIDS="$PIDS $!"
done

ALLFAILED=1
ANYFAILED=0
for PID in $PIDS ; do
    wait $PID
    if [ "$?" != "0" ]; then
        ANYFAILED=1
    else
        ALLFAILED=0
    fi
done

[[ "1" == "1" ]] && echo "All workers done"
if [ "$FAILONANY" == "1" ]; then
    exit $ANYFAILED
else
    exit $ALLFAILED
fi