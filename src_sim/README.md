#### MuonGun Simulation

**Step 1**:
* Generate muon near dectector volume
```.sh
python submit_muon.py
```

**Step 2**:
* Cherenkov photon propagation
```.sh
python submit_photon.py
```

**Step 3**:
* Simulate detector electronics
```.sh
python submit_daq.py
```

**Step 4**:
* Linefit Reconstruction
```.sh
python submit_daq.py
```