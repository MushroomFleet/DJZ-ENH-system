import os

class ZenkaiENH:
    @classmethod
    def INPUT_TYPES(cls):
        enh_folder = os.path.join(os.path.dirname(__file__), 'ENH-store')
        
        # Create the ENH-store folder if it doesn't exist
        if not os.path.exists(enh_folder):
            os.makedirs(enh_folder)
        
        # Get all .md files from the ENH-store folder
        md_files = [f for f in os.listdir(enh_folder) if f.endswith('.md')]
        
        # If no .md files exist, provide a default option
        if not md_files:
            md_files = ["No .md files found"]
        
        return {
            "required": {
                "enh_file": (md_files,),
            }
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "load_enh_prompt"
    CATEGORY = "DJZ-Nodes"

    def load_enh_prompt(self, enh_file):
        enh_folder = os.path.join(os.path.dirname(__file__), 'ENH-store')
        file_path = os.path.join(enh_folder, enh_file)
        
        # Handle case where no .md files exist
        if enh_file == "No .md files found":
            return ("Please add .md files to the ENH-store folder",)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return (content,)
        except FileNotFoundError:
            return (f"Error: File '{enh_file}' not found in ENH-store folder",)
        except Exception as e:
            return (f"Error reading file: {str(e)}",)

    @classmethod
    def IS_CHANGED(cls, enh_file):
        enh_folder = os.path.join(os.path.dirname(__file__), 'ENH-store')
        file_path = os.path.join(enh_folder, enh_file)
        
        # Return file modification time to detect changes
        try:
            return os.path.getmtime(file_path)
        except:
            return 0

NODE_CLASS_MAPPINGS = {
    "ZenkaiENH": ZenkaiENH
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ZenkaiENH": "Zenkai-ENH"
}