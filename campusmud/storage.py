# Storage module - handles JSON file reading and writing with atomic saves
import json
import os
import tempfile


class Storage:
    """
    Handles loading and saving JSON data files with atomic write protection.
    """
    def __init__(self):
        pass
        
    def get_data(self, file):
        """
        Load data from a JSON file. Returns empty dict if file doesn't exist or is invalid.
        """
        if not os.path.exists(file):
            return {}
        with open(file, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
            
    def save_data(self, file, obj):
        """
        Save data to a JSON file using atomic write (tempfile + rename).
        Merges with existing data if both are dicts or lists.
        """
        data = self.get_data(file)

        if isinstance(data, dict) and isinstance(obj, dict):
            data.update(obj)
        elif isinstance(data, list) and isinstance(obj, list):
            data.extend(obj)
        else:
            data = obj 

        # Atomic save: write to temp file, then rename
        dir_name = os.path.dirname(file) or '.'
        fd, temp_path = tempfile.mkstemp(dir=dir_name, prefix='.tmp_', suffix='.json')
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            os.replace(temp_path, file)
        except:
            os.close(fd)
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise
