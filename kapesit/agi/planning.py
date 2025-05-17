class Task:
    def __init__(self, name, subtasks=None):
        self.name = name
        self.subtasks = subtasks or []
        self.completed = False
    def add_subtask(self, subtask):
        self.subtasks.append(subtask)
    def mark_complete(self):
        self.completed = True
class Planner:
    def __init__(self):
        self.tasks = []
    def add_task(self, task):
        self.tasks.append(task)
    def plan(self):
        plan = []
        for task in self.tasks:
            plan.extend(self._expand(task))
        return plan
    def _expand(self, task):
        if not task.subtasks:
            return [task.name]
        result = []
        for sub in task.subtasks:
            result.extend(self._expand(sub))
        return result 