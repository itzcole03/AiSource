class TaskPrioritizationSystem:
    def __init__(self):
        self.tasks = []

    def add_task(self, task):
        self.tasks.append(task)

    def get_highest_priority_task(self):
        return self.tasks[0] if self.tasks else None

    # Other methods for managing tasks, etc.