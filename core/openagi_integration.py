import openagi.client as client

class OpenAGIServiceOrchestration:
    def __init__(self, service_orchestration_config, service_integration_config):
        self.service_orchestration = client.ServiceOrchestrationClient(**service_orchestration_config)
        self.service_integration = client.ServiceIntegrationClient(**service_integration_config)

    def create_service_orchestration(self):
        return self.service_orchestration

    def create_service_integration(self):
        return self.service_integration


# Load configuration files
service_orchestration_config = openagi.load_configuration("service_orchestration.json")
service_integration_config = openagi.load_configuration("service_integration.json")

# Create service orchestrations and integrations
service_orchestration = OpenAGIServiceOrchestration(service_orchestration_config, service_integration_config)

# Start the service orchestration component
service_orchestration.create_service_orchestration()

# Start the service integration component
service_orchestration.create_service_integration()

# Example usage
request = client.Request("GET", "example_url")
response = service_orchestration.send_request(request)
print(f"Response: {response}")