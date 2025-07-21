# Smartank

Smartank is an IoT device that connects to ORP, pH, and Temperature meters, providing real-time monitoring and data logging.

## Technologies Used

- Flask (Web server)
- Prometheus (Metrics collection)
- Grafana (Visualization)

## Setup: Smartank Server

1. **Install Flask**  
   Follow this guide: [Python Webserver with Flask and Raspberry Pi](https://towardsdatascience.com/python-webserver-with-flask-and-raspberry-pi-398423cc6f5d)

2. **Configure RedseaFlask Service**  
   Set up the Flask service for data collection and API endpoints.

3. **Schedule Data Recognition**  
   Use a cron job to run `RedseaReader` for periodic data recognition and logging.

## Setup: Monitoring Server

1. **Install Grafana**  
   [Grafana Installation Guide](https://grafana.com/tutorials/install-grafana-on-raspberry-pi/)

2. **Install Prometheus**  
   [Prometheus Installation Guide](http://www.d3noob.org/2020/02/installing-prometheus-and-grafana-on.html)

3. **Configure Prometheus**  
   Set Prometheus to scrape metrics from the RedseaFlask service.

---

You can also refer to the [documentation](https://www.mitang.me/meter-reader/) for the idea
