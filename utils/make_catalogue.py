#!/usr/bin/env python3
import ijson               # pip install ijson[yajl2_c]
import json
import pickle
import threading
import queue
from collections import defaultdict
from tqdm import tqdm
from unidecode import unidecode  # pip install Unidecode

# ——— File paths ———
input_json_path       = '/home/shanchun123/20250331_nodes_and_edges_remapped_kgcleaned_nomappedentitytype.json'
output_catalogue_json = '/home/shanchun123/catalogue_test.json'
output_catalogue_pkl  = '/home/shanchun123/catalogue_test.pkl'

# ——— Config ———
entity_columns = ['entity1_disamb', 'entity2_disamb']
keys           = list('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ')
key_set        = set(keys)

# Shared catalogue: [keys, { key → set(entities) }]
catalogue      = [keys, {k: set() for k in keys}]
catalogue_lock = threading.Lock()

# Queue and sentinel
record_queue = queue.Queue(maxsize=1000)
SENTINEL     = object()

def worker(batch_size=1000):
    """
    Worker thread:
    - Pull records off the queue
    - Transliterate → scan for first ASCII alnum → bucket
    - Batch‑flush into the shared catalogue under a lock
    """
    local_catalogue = defaultdict(set)
    count = 0

    while True:
        record = record_queue.get()
        if record is SENTINEL:
            # final flush
            if local_catalogue:
                with catalogue_lock:
                    for k, s in local_catalogue.items():
                        catalogue[1][k].update(s)
                local_catalogue.clear()
            record_queue.task_done()
            break

        for col in entity_columns:
            ent = record.get(col)
            # skip non-strings and None
            if not isinstance(ent, str):
                continue
            ent = ent.strip()
            # skip empty or single-character names
            if len(ent) <= 1:
                continue

            # 1) transliterate to ASCII
            ent_ascii = unidecode(ent)

            # 2) manual scan for first ASCII alnum in key_set
            for ch in ent_ascii:
                chu = ch.upper()
                if chu in key_set:
                    local_catalogue[chu].add(ent)
                    break

        count += 1
        if count >= batch_size:
            with catalogue_lock:
                for k, s in local_catalogue.items():
                    catalogue[1][k].update(s)
            local_catalogue.clear()
            count = 0

        record_queue.task_done()

# ——— Start workers ———
num_workers = 4
threads = []
for _ in range(num_workers):
    t = threading.Thread(target=worker, args=(1000,))
    t.daemon = True
    t.start()
    threads.append(t)

# ——— Producer: read & enqueue ———
with open(input_json_path, 'rb') as f:
    for record in tqdm(ijson.items(f, 'item'), desc='Reading records'):
        record_queue.put(record)

# ——— Signal shutdown ———
for _ in range(num_workers):
    record_queue.put(SENTINEL)

# ——— Wait for completion ———
record_queue.join()
for t in threads:
    t.join()

# ——— Finalize & dump ———
# Convert sets → lists for JSON serialization,
# with non‑alphanumeric‑starting entities at the back.
for k in catalogue[1]:
    lst = list(catalogue[1][k])
    # alnum-first (False=0), non-alnum-last (True=1), then case-insensitive sort
    lst.sort(key=lambda x: (not x[0].isalnum(), x.lower()))
    catalogue[1][k] = lst

# JSON
with open(output_catalogue_json, 'w') as f:
    json.dump(catalogue, f, indent=4)
print(f"Catalogue saved as JSON at: {output_catalogue_json}")

# Pickle
with open(output_catalogue_pkl, 'wb') as f:
    pickle.dump(catalogue, f)
print(f"Catalogue saved as pickle at: {output_catalogue_pkl}")