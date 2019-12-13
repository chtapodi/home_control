# spacial_volume_control
## volume_control
This is a project which scales all the volumes of my chromecasts so they are of equal volume at a specific point.
Each device must have assigned 2D coordinates, and a foci must be chosen using the same coordinate system. 
The units do not matter as long as they are all the same.

Volume can be set at the foci via the  '-v' flag


### interactive mode
'-i'
This mode allows you to change the volume foci and base volume via the keyboard

### loop mode
'-l'
This cleanly updates all device volumes at the foci to match that of the closest device.

## TODO
Add config file loading 
Refactor into class
Add spacial tracking and vary volume as I move
