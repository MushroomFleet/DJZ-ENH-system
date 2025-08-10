"""
DJZ-ENH: JSON processing nodes for ComfyUI
"""

import os
import importlib.util
import sys

# Initialize empty dictionaries for all mappings
NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

# Helper function to safely import a module
def import_module_safely(module_name, file_path):
    try:
        if os.path.exists(file_path):
            # Use importlib to import the module from file path
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if spec:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Get the mappings if they exist
                class_mappings = getattr(module, 'NODE_CLASS_MAPPINGS', {})
                display_mappings = getattr(module, 'NODE_DISPLAY_NAME_MAPPINGS', {})
                
                # Update our mappings
                NODE_CLASS_MAPPINGS.update(class_mappings)
                NODE_DISPLAY_NAME_MAPPINGS.update(display_mappings)
                
                print(f"Successfully imported {module_name} nodes")
                return True
        else:
            print(f"File not found: {file_path}")
            return False
    except Exception as e:
        print(f"Error importing {module_name}: {e}")
        return False

# Get the current directory - using direct path rather than __file__
current_dir = os.path.abspath(os.path.dirname(os.path.realpath(__file__)) if '__file__' in globals() else os.getcwd())

# List of modules to import
modules = [
    ('ENH_JSON', 'ENH_JSON.py'),
    ('ZenkaiENH', 'ZenkaiENH.py'),
]

# Import each module
for module_name, file_name in modules:
    module_path = os.path.join(current_dir, file_name)
    import_module_safely(module_name, module_path)

# Print the available nodes for debugging
print(f"Available nodes: {list(NODE_CLASS_MAPPINGS.keys())}")
print(f"Available display names: {list(NODE_DISPLAY_NAME_MAPPINGS.keys())}")

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
