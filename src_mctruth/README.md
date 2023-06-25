#### Track Reconstruction

**Step 1**:
* Run track reco 
```.sh
python submit_mctruth.py
```

**Step 2**:
* Get LDirA selection
```.sh
python submit_selection.py
```

**Step 3**:
* Get hdf5 data from i3files
```.sh
python submit_hdfdata.py
```