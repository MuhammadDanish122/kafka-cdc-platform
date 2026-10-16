"""Reference consumer loop: commit Kafka offsets only after ClickHouse confirms the write.

Written for this showcase. Not production code.
"""
from kafka import KafkaConsumer


class BatchFailed(Exception):
    pass


def run(topic, group_id, bootstrap, write_batch, batch_size=5000):
    consumer = KafkaConsumer(
        topic,
        group_id=group_id,
        bootstrap_servers=bootstrap,
        enable_auto_commit=False,      # we decide when an offset is safe
        auto_offset_reset="earliest",  # a new group never skips history
    )
    while True:
        polled = consumer.poll(timeout_ms=1000, max_records=batch_size)
        rows = [msg.value for msgs in polled.values() for msg in msgs]
        if not rows:
            continue                   # nothing written, nothing to commit
        try:
            write_batch(rows)          # must raise unless ClickHouse acked
        except Exception as exc:
            consumer.close(autocommit=False)
            raise BatchFailed(f"{topic}: stopping, offsets not committed") from exc
        consumer.commit()              # only now is the batch done
