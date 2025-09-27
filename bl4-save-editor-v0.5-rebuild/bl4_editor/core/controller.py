# Updated bl4_editor/core/controller.py
from typing import Dict, Any
from bl4_editor.core import logger

class TabController:
    """Enhanced controller with proper data flow management"""
    
    def __init__(self, tabs: Dict[str, Any]):
        self.tabs = tabs
    
    def load_into_tabs(self, data: Dict[str, Any]):
        """Load save data into appropriate tabs"""
        if not isinstance(data, dict):
            logger.warning("Data is not a dictionary")
            return
        # Load character data (state goes to character)
        if 'character' in self.tabs and 'state' in data:
            try:
                self.tabs['character'].load_data({'state': data['state']})
                logger.info("Loaded character data")
            except Exception as e:
                logger.warning(f"Character tab load failed: {e}")

        # For items and other tabs, prefer data under 'state' when present
        state_root = data.get('state', data)

        # Load items data - pass the full state/profile dict so ItemsTab can preserve originals
        if 'items' in self.tabs:
            try:
                # if this is a profile save, items may live under data['shared']
                if 'shared' in data and isinstance(data['shared'], dict):
                    self.tabs['items'].load_data(data)
                else:
                    self.tabs['items'].load_data(state_root)
                logger.info("Loaded items data")
            except Exception as e:
                logger.warning(f"Items tab load failed: {e}")

        # Load other tab data (search both top-level and state)
        for tab_name in ['progression', 'stats', 'world', 'unlockables', 'profile']:
            if tab_name in self.tabs:
                # prefer state_root then top-level
                payload = None
                if isinstance(state_root, dict) and tab_name in state_root:
                    payload = state_root[tab_name]
                elif tab_name in data:
                    payload = data[tab_name]
                # If no specific payload found for the profile tab, but the data looks
                # like a profile (contains inputprefs/ui/onlineprefs/domains/shared),
                # pass the whole data so the ProfileTab can interpret it.
                if payload is None and tab_name == 'profile':
                    if isinstance(data, dict) and any(k in data for k in ('inputprefs', 'ui', 'onlineprefs', 'domains', 'shared')):
                        payload = data

                if payload is not None and hasattr(self.tabs[tab_name], 'load_data'):
                    try:
                        self.tabs[tab_name].load_data(payload)
                        logger.info(f"Loaded {tab_name} data")
                    except Exception as e:
                        logger.warning(f"Failed loading {tab_name}: {e}")
    
    def save_from_tabs(self, data: Dict[str, Any]):
        """Collect data from tabs back into the main data structure"""
        for tab_name, tab_instance in self.tabs.items():
            if hasattr(tab_instance, 'save_data'):
                try:
                    tab_data = tab_instance.save_data()
                    if tab_data:
                        # Merge tab data back into main data
                        if tab_name == 'character':
                            # Character tab returns {'state': {...}}
                            if isinstance(tab_data, dict) and 'state' in tab_data:
                                data['state'] = tab_data['state']
                        elif tab_name == 'items':
                            # Items tab returns the full modified data structure
                            if isinstance(tab_data, dict):
                                data.update(tab_data)
                        else:
                            # Other tabs return their section data directly
                            data[tab_name] = tab_data
                        logger.debug(f"Saved data from {tab_name} tab")
                except Exception as e:
                    logger.error(f"Error saving data from {tab_name} tab: {e}")
