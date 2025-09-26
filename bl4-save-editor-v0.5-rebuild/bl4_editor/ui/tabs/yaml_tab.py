class YamlTab:
    def __init__(self): self.text=''
    def set_yaml(self,data):
        import yaml as _yaml
        self.text = _yaml.safe_dump(data, sort_keys=False, allow_unicode=True)
    def get_yaml(self):
        import yaml as _yaml
        return _yaml.safe_load(self.text) if self.text else {}
