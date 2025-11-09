# Copyright 2025 Marc Duclusaud & Grégoire Passault

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:

#     http://www.apache.org/licenses/LICENSE-2.0

import glob
from copy import deepcopy
import os
import json
import numpy as np
import argparse

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("--raw", type=str, required=True)
arg_parser.add_argument("--logdir", type=str, required=True)
arg_parser.add_argument("--dt", type=float, default=0.005)
args = arg_parser.parse_args()

# Create output directory if it doesn't exist
os.makedirs(args.logdir, exist_ok=True)

# Check if raw directory exists and has files
if not os.path.exists(args.raw):
    print(f"Error: Raw data directory '{args.raw}' does not exist!")
    print(f"Current directory: {os.getcwd()}")
    exit(1)

raw_files = glob.glob(f"{args.raw}/*.json")
if not raw_files:
    print(f"Error: No JSON files found in '{args.raw}'")
    print(f"Make sure you have collected raw data first using:")
    print(f"  python -m bam.hiwonder.all_record_board ...")
    exit(1)

print(f"Found {len(raw_files)} files to process")
print(f"Output directory: {args.logdir}")
print()

for logfile in raw_files:
    data = json.load(open(logfile))
    data_output = deepcopy(data)
    data_output["entries"] = []
    data_output["dt"] = args.dt

    duration = data["entries"][-1]["timestamp"]
    print(f"* Processing {logfile} with duration {duration:.2f}s")
    ts = np.arange(0.0, duration, args.dt)
    frame = 0

    for t in ts:
        while t > data["entries"][frame + 1]["timestamp"]:
            frame += 1
        entry_1 = data["entries"][frame]
        entry_2 = data["entries"][frame + 1]
        new_entry = {}

        for key in entry_1:
            if key == "timestamp":
                continue
            new_entry[key] = entry_1[key] + (entry_2[key] - entry_1[key]) * (
                t - entry_1["timestamp"]
            ) / (entry_2["timestamp"] - entry_1["timestamp"])

        new_entry["torque_enable"] = True if (new_entry["torque_enable"] > 0.5) else False
        new_entry["timestamp"] = t

        data_output["entries"].append(new_entry)

    filename = os.path.basename(logfile)
    output_filename = f"{args.logdir}/{filename}"
    json.dump(data_output, open(output_filename, "w"))
    print(f"  Saved: {output_filename}")

print()
print(f"✓ Processing complete! {len(raw_files)} files processed.")
print(f"  Output directory: {args.logdir}/")
print(f"  Next step: python -m bam.plot --actuator htd45h --logdir {args.logdir}")
