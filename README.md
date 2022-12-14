# FCC Radiation

Investigation of radiation in FCC caverns.

## Directory structure

`input` --- input files needed to run the full simulation. ATM it stores only
beamloss input files. Other files are loaded from `/opt` directory.

`output` --- root files, results of the full simulation.

`plots` --- plots generated from `output` root files.

`run` --- steering and batch running scripts.

## Running in Batch mode

```sh
cd run
# Processes
for i in {1..120}; do echo "./rrr_beamlosses ${i}" | batch; done
# Beamloss
for i in {00..32}; do echo "./rrr_beamlosses ${i}" | batch; done
```
