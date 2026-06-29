from locust import HttpUser, TaskSet, task, between


class SimulatorUser(HttpUser):
    wait_time = between(1, 3)

    @task(2)
    def home(self):
        self.client.get('/')

    @task(1)
    def payment_stats(self):
        self.client.get('/stats/')

    @task(1)
    def payment_metrics(self):
        self.client.get('/metrics/')

    @task(1)
    def health(self):
        self.client.get('/health/')
