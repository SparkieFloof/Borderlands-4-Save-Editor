import os, tempfile, shutil, subprocess, yaml

class PatchedLoader(yaml.FullLoader):
    pass

def _unknown_tag_constructor(loader, tag_suffix, node):
    # for unknown tags, return plain Python structures
    if isinstance(node, yaml.ScalarNode):
        return loader.construct_scalar(node)
    if isinstance(node, yaml.SequenceNode):
        return loader.construct_sequence(node)
    if isinstance(node, yaml.MappingNode):
        return loader.construct_mapping(node)
    return None

yaml.add_multi_constructor('!', _unknown_tag_constructor, Loader=PatchedLoader)

def open_file(path, userid=None):
    path = os.path.abspath(path)
    if path.lower().endswith(('.yaml','.yml')):
        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.load(f, Loader=PatchedLoader)
        return path, data
    if path.lower().endswith('.sav'):
        if not userid:
            raise RuntimeError("UserID required to open .sav")
        tmp = os.path.join(tempfile.gettempdir(), os.path.basename(path) + '.yaml')
        exe = 'bl4-crypt-cli.exe' if os.path.exists(os.path.join(os.getcwd(),'bl4-crypt-cli.exe')) else 'bl4-crypt-cli'
        cmd = [exe, '-i', path, '-o', tmp, '-u', userid]
        subprocess.run(cmd, check=True)
        with open(tmp, 'r', encoding='utf-8') as f:
            data = yaml.load(f, Loader=PatchedLoader)
        return tmp, data
    raise RuntimeError('Unsupported file type')
