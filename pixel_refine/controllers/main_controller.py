from pixel_refine.models.database_manager import DatabaseManager
from pixel_refine.controllers.algorithm_controller import AlgorithmController
from kivy.clock import Clock


from pixel_refine.logic.image_handler import ImageHandler

class MainController:
    def __init__(self):
        self.db_path = "pixel_refine_database.db"
        self.db_manager = DatabaseManager(self.db_path)
        self.image_handler = ImageHandler(self.db_manager)
        self.algorithm_controller = AlgorithmController(self)
        self.view = None  # Reference to the main view (set later)

    def set_view(self, view):
        self.view = view
        self.refresh_project_list()

    def handle_import(self):
        if self.view:
            self.view.show_file_chooser(self.on_files_selected)

    def on_files_selected(self, selection):
        if not selection:
            return
        
        # Define callbacks for UI updates
        callbacks = {
            'on_progress': self.update_progress,
            'on_completion': self.on_import_complete,
            'on_error': self.on_import_error,
            'on_message': self.show_message
        }
        
        self.image_handler.process_import(selection, callbacks)

    def on_import_complete(self, total_items):
        print(f"Import completed: {total_items} items")
        self.refresh_project_list()
        self.update_progress(100, "Import Complete")

    def on_import_error(self, error_msg):
        print(f"Import error: {error_msg}")
        self.show_message("Error", error_msg)

    def show_message(self, title, message):
        if self.view:
            self.view.show_message(title, message)

    def handle_item_selection(self, item_id):
        print(f"Item selected: {item_id}")
        # Load project details from DB

    def add_project(self, name):
        return self.db_manager.create_new_panorama_project(name)

    def get_projects(self):
        return self.db_manager.get_all_panorama_projects()

    def refresh_project_list(self):
        if self.view and hasattr(self.view, "selector"):
            projects = self.get_projects()
            # Update selector UI - this logic needs to be in the View or bound via properties
            # For Kivy, usually we update a ListProperty that the View observes
            # For now, let's just print
            print(f"Projects: {projects}")

    def run_process(self, settings):
        print(f"Running process with settings: {settings}")
        # Example: Get current project ID (needs state management)
        current_project_id = 1  # Placeholder
        method = settings.get("method", "AKAZE")

        self.algorithm_controller.run_alignment(
            current_project_id, method, self.on_process_complete
        )

    def update_progress(self, value, message):
        print(f"Progress: {value}% - {message}")
        if self.view and hasattr(self.view, "workspace"):
            # Update ViewerPanel loading state
            if value < 100:
                self.view.workspace.viewer.show_loading(message)
            else:
                self.view.workspace.viewer.show_grid()  # Go back to grid when done

    def on_process_complete(self, success):
        print(f"Process finished: {success}")
