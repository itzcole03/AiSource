class AutoGPTTaskExecutor(Component):
    def __init__(self, autoGPT_client, model_id, task_definition):
        # Initialize AutoGPT client and model ID
        self.autoGPT_client = autoGPT_client
        self.model_id = model_id
        self.task_definition = task_definition