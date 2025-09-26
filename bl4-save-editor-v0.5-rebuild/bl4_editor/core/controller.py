class TabController:
    def __init__(self, tabs: dict):
        self.tabs = tabs
    def load_into_tabs(self, data: dict):
        for name, tab in self.tabs.items():
            if hasattr(tab, 'load_data'):
                tab.load_data(data.get(name, {}))
