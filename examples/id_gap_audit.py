"""Low-load id-gap audit: compare PK bucket counts, pull ids only where they differ.

Written for this showcase. `src` and `dst` are callables that run one SQL query and return rows.
"""
import time

BUCKET = 20_000


def audit(table, pk, src, dst, max_id, pause_s=0.5):
    gaps = []
    for lo in range(0, max_id + 1, BUCKET):
        hi = lo + BUCKET
        where = f"{pk} >= {lo} AND {pk} < {hi}"
        # MAX_EXECUTION_TIME keeps each source query bounded
        n_src = src(f"SELECT /*+ MAX_EXECUTION_TIME(5000) */ COUNT(*) FROM {table} WHERE {where}")[0][0]
        n_dst = dst(f"SELECT uniqExact({pk}) FROM {table} WHERE {where}")[0][0]
        if n_src != n_dst:
            a = {r[0] for r in src(f"SELECT {pk} FROM {table} WHERE {where}")}
            b = {r[0] for r in dst(f"SELECT {pk} FROM {table} WHERE {where}")}
            gaps.extend(sorted(a - b))
        time.sleep(pause_s)            # give production room to breathe
    return gaps
