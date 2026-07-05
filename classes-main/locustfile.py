from locust import HttpUser, task, between
import os


class SimulatorUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """Called when a user starts. Can be used for login or initial setup."""
        pass

    @task(2)
    def home(self):
        """Test home endpoint"""
        self.client.get('/', name='/')

    @task(1)
    def payment_stats(self):
        """Test payment stats endpoint"""
        response = self.client.get('/stats/', name='/stats/')
        if response.status_code != 200:
            self.client.get('/api/kpi/dashboard/', name='/api/kpi/dashboard/')

    @task(1)
    def payment_metrics(self):
        """Test payment metrics endpoint"""
        self.client.get('/metrics/', name='/metrics/')

    @task(1)
    def health_check(self):
        """Test health check endpoint"""
        self.client.get('/health/', name='/health/')
