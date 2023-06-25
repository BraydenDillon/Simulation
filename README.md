## Simulation and Reconstruction

Example script to generate MuonGun simualation and Reconstruction


create the following directories in `sim0002`

```.sh
mkdir -p daqfiles  eventfiles  gcdfile  linefit  photonfiles  reco_mctruth  reco_spline  src_mctruth  src_sim  src_spline
```

**src_sim**:
scripts to generate MuoGun simulation

```.sh
mkdir -p error log out
```

**src_mctruth**:

scripts run track reconstruction seeded with mctruth

```.sh
mkdir -p error log out
```

**src_spline**:

script to run track reconstruction seed with linefit followed by convolution

```.sh
mkdir -p error log out
```

**Note***: Rename directories and paths accordingly