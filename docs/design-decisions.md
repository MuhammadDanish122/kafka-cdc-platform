# Design decisions

## Why ack-then-commit
The old consumers committed offsets before the write landed. If ClickHouse rejected the batch or the process died, those rows were gone. Two more issues made it worse: groups that reset to `latest` skipped history, and empty polls were committed as success. Now a batch is only committed after the insert returns, and any failure stops the consumer so it shows up in alerts instead of in a missing-data report weeks later.

## Why versioned tables
CDC delivers updates far more than inserts here (~80/20). ReplacingMergeTree-style tables keyed on the primary key with a version column let me insert every change and let ClickHouse keep the latest one. Dedup jobs use lightweight deletes rather than mutations to keep the load down.

## Why read the binlog for metrics
Sampling counters drifts. Reading the binlog in order with a checkpoint gives exact per-table, per-minute counts and picks up where it left off after a restart.

## Auditing production safely
Comparing source and target row-by-row on 200+ tables would hammer MySQL. The audit counts ids in ~20k-wide PK buckets, one bounded query at a time with time limits and pauses, and only pulls actual ids for buckets where counts differ.
