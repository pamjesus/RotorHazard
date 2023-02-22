## OBS_Websocks
 OBS websocks plugin for Rotorhazard to allow control recording at start and stop of the race.

## Features
* Start/Stop OBS recording at every race. 
* Star recording before race starts (parameter in milliseconds)
* Restart connection to OBS in case of a failed call to the Webservice
* When active, a start/stop recording failure raises a high-priority message in the front end.
 

### TODO
  * Adapt to Live model. i.e. Changing scenes based on Rotorhazard timer events.

### Install

 pip install -r .\requirements.txt

Add parameters at the bottom of the config.json file. You can use the template at config-dist.json in this plugIn. 

Set your IP, port, and password. 
This plug-in is active where ENABLED is set to true.
The parameter PRE_START is optional, and set's the time to start recording before the race starts. 