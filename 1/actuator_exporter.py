#!/usr/bin/env python3
"""
Simple Actuator to Prometheus metrics exporter
Converts Spring Boot Actuator metrics to Prometheus format
"""

import json
import requests
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

ACTUATOR_BASE_URL = "http://localhost:7011/actuator"
EXPORTER_PORT = 7778

class ActuatorExporter(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/metrics":
            try:
                metrics = self.get_actuator_metrics()
                prometheus_metrics = self.convert_to_prometheus(metrics)
                
                self.send_response(200)
                self.send_header('Content-type', 'text/plain; version=0.0.4; charset=utf-8')
                self.end_headers()
                self.wfile.write(prometheus_metrics.encode())
            except Exception as e:
                self.send_error(500, f"Error getting metrics: {str(e)}")
        elif self.path == "/health":
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b"OK")
        else:
            self.send_error(404)
    
    def get_actuator_metrics(self):
        """Get list of available metrics from Actuator"""
        response = requests.get(f"{ACTUATOR_BASE_URL}/metrics", timeout=5)
        response.raise_for_status()
        metrics_list = response.json().get('names', [])
        
        metrics_data = {}
        important_metrics = [
            'jvm.memory.used', 'jvm.memory.max', 'jvm.memory.committed',
            'jvm.threads.live', 'jvm.threads.peak', 'jvm.threads.daemon',
            'jvm.gc.memory.allocated', 'jvm.gc.memory.promoted', 'jvm.gc.pause',
            'jvm.gc.live.data.size', 'jvm.gc.max.data.size',
            'system.cpu.usage', 'process.cpu.usage', 'system.load.average.1m',
            'hikaricp.connections.active', 'hikaricp.connections.idle', 
            'hikaricp.connections.max', 'hikaricp.connections.min',
            'hikaricp.connections.pending', 'hikaricp.connections.timeout',
            'hikaricp.connections.usage', 'hikaricp.connections.creation',
            'rabbitmq.connections', 'rabbitmq.channels', 'rabbitmq.published',
            'rabbitmq.consumed', 'rabbitmq.acknowledged', 'rabbitmq.rejected',
            'tomcat.sessions.active.current', 'tomcat.sessions.active.max',
            'tomcat.sessions.created', 'tomcat.sessions.expired',
            'spring.integration.channels', 'spring.integration.handlers',
            'process.uptime', 'process.files.open', 'process.files.max'
        ]
        
        for metric in metrics_list:
            if any(important in metric for important in important_metrics):
                try:
                    metric_response = requests.get(f"{ACTUATOR_BASE_URL}/metrics/{metric}", timeout=5)
                    if metric_response.status_code == 200:
                        metrics_data[metric] = metric_response.json()
                except:
                    continue
                    
        return metrics_data
    
    def convert_to_prometheus(self, metrics_data):
        """Convert Actuator metrics to Prometheus format"""
        prometheus_output = []
        prometheus_output.append("# Actuator Metrics converted to Prometheus format")
        prometheus_output.append(f"# Scraped at {int(time.time())}")
        
        for metric_name, metric_data in metrics_data.items():
            try:
                prometheus_name = metric_name.replace('.', '_').replace('-', '_')
                
                if 'measurements' in metric_data:
                    for measurement in metric_data['measurements']:
                        labels = []
                        if 'availableTags' in metric_data:
                            for tag in metric_data.get('availableTags', []):
                                if 'values' in tag and tag['values']:
                                    labels.append(f'{tag["tag"]}="{tag["values"][0]}"')
                        
                        label_str = '{' + ','.join(labels) + '}' if labels else ''
                        value = measurement.get('value', 0)
                        statistic = measurement.get('statistic', '').lower()
                        
                        if statistic and statistic != 'value':
                            final_name = f"{prometheus_name}_{statistic}"
                        else:
                            final_name = prometheus_name
                            
                        prometheus_output.append(f"# HELP {final_name} {metric_data.get('description', '')}")
                        prometheus_output.append(f"# TYPE {final_name} gauge")
                        prometheus_output.append(f"{final_name}{label_str} {value}")
                        
            except Exception as e:
                print(f"Error processing metric {metric_name}: {e}")
                continue
        
        return '\n'.join(prometheus_output) + '\n'

    def log_message(self, format, *args):
        """Suppress default HTTP server logging"""
        pass

def main():
    print(f"Starting Actuator Exporter on port {EXPORTER_PORT}")
    print(f"Metrics endpoint: http://localhost:{EXPORTER_PORT}/metrics")
    print(f"Health endpoint: http://localhost:{EXPORTER_PORT}/health")
    
    server = HTTPServer(('', EXPORTER_PORT), ActuatorExporter)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down exporter...")
        server.shutdown()

if __name__ == "__main__":
    main()
