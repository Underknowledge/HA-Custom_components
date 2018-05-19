# Custom_component for [ha-dockermon](https://github.com/philhawthorne/ha-dockermon)
![Version](https://img.shields.io/badge/version-1.0.1-green.svg?style=for-the-badge)

A custom component which allows you to interact with [ha-dockermon.](https://github.com/philhawthorne/ha-dockermon)

To start using this make sure you have [ha-dockermon](https://github.com/philhawthorne/ha-dockermon) running.  
After that put `/custom_components/switch/hadockermon.py` here:  
`<config directory>/custom_components/switch/hadockermon.py`  
   
Example configuration.yaml:  
```yaml
switch:
  - platform: hadockermon
    host: 192.168.1.50
    port: 8126
    stats: true
    exclude:
      - NGINX
      - ha-dockermon
```
**configuration variables:**  
**host (Required):** The IP address of your Docker host.  
**port (Optional):** The port that the service is exposed on.  
**stats (Optional):** Show memory and network usage of the containers, this does _not_ work on every docker host.  
**exclude (Optional):** A list of Docker containers you want to exclude.  
  
#### Sample overview
![Samble overview](overview.PNG)  
[Demo](https://ha-test-hadockermon.halfdecent.io)