class ProjectModel:
    def __init__(self):
        self.projects = []

    def add_project(self, name):
        project = {"id": len(self.projects), "name": name}
        self.projects.append(project)
        return project

    def get_projects(self):
        return self.projects

    def delete_project(self, project_id):
        self.projects = [p for p in self.projects if p["id"] != project_id]
