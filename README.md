# Smartank
A IOT device, which is enabled to connect to ORP, PH, Temperature meter.

### Technologies:
FLASK, Prometheus, Grafana

### Setup Smartank server
- Install Flask:
https://towardsdatascience.com/python-webserver-with-flask-and-raspberry-pi-398423cc6f5d
- Setup RedseaFlask service
- Setup cron job for RedseaReader to recognize the data

### Setup Monitoring server
- Install Grafana https://grafana.com/tutorials/install-grafana-on-raspberry-pi/
- Install Prometheus http://www.d3noob.org/2020/02/installing-prometheus-and-grafana-on.html
- Config Prometheus to scrap RedseaFalsk service
