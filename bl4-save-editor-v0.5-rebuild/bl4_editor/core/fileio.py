import os, tempfile, shutil, subprocess, yaml, time
from bl4_editor.core import crypt as crypt_mod
from bl4_editor.core import logger

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
    # ensure local temp folder exists in workspace
    workspace_temp = os.path.join(os.getcwd(), 'temp')
    os.makedirs(workspace_temp, exist_ok=True)

    if path.lower().endswith(('.yaml','.yml')):
        # copy YAML into workspace temp for editing
        base = os.path.basename(path)
        # add timestamp to avoid clobbering
        dest = os.path.join(workspace_temp, f"{int(time.time())}_{base}")
        shutil.copy2(path, dest)
        with open(dest, 'r', encoding='utf-8') as f:
            data = yaml.load(f, Loader=PatchedLoader)
        return dest, data
    if path.lower().endswith('.sav'):
        if not userid:
            raise RuntimeError("UserID required to open .sav")
        tmp = os.path.join(workspace_temp, os.path.basename(path) + '.yaml')
        # prefer bundled exe in workspace if present
        exe = os.path.join(os.getcwd(), 'bl4-crypt-cli.exe') if os.path.exists(os.path.join(os.getcwd(),'bl4-crypt-cli.exe')) else 'bl4-crypt-cli'
        crypt = crypt_mod.CryptWrapper(exe_path=exe, logger=logger)
        ok = crypt.decrypt(path, tmp, userid=userid)
        if not ok:
            raise RuntimeError('Decryption failed (see logs)')
        with open(tmp, 'r', encoding='utf-8') as f:
            data = yaml.load(f, Loader=PatchedLoader)
        return tmp, data
    raise RuntimeError('Unsupported file type')


def safe_write_yaml(path, data, atomic=True, make_backup=False):
    """Write YAML to path while preventing PyYAML from emitting anchors/aliases.

    To avoid emitting YAML anchors (e.g. "&id001"), we normalize the data
    by round-tripping through JSON where possible to break shared object
    identity. We then dump using a dumper that ignores aliases.

    Parameters:
    - path: destination file path
    - data: Python structure to dump
    - atomic: if True, write to a temp file in the same directory and os.replace
              into the destination (safer for overwrites). If False, write
              directly to `path`.
    - make_backup: if True and the destination exists, create a timestamped
                   backup before replacing it.
    """
    class NoAliasDumper(yaml.SafeDumper):
        def ignore_aliases(self, _data):
            return True

    # Try to normalize via JSON to break Python object identity which causes
    # PyYAML to emit anchors. Fall back to a deepcopy if JSON fails.
    norm = None
    try:
        import json
        norm = json.loads(json.dumps(data))
    except Exception:
        # fallback: use yaml round-trip to get a fresh structure
        try:
            norm = yaml.load(yaml.dump(data), Loader=PatchedLoader)
        except Exception:
            # last resort: deepcopy
            import copy
            norm = copy.deepcopy(data)

    dest_dir = os.path.dirname(os.path.abspath(path)) or '.'
    os.makedirs(dest_dir, exist_ok=True)

    def _write_to(pth):
        with open(pth, 'w', encoding='utf-8') as f:
            yaml.dump(norm, f, Dumper=NoAliasDumper, sort_keys=False, allow_unicode=True)

    if atomic:
        # prepare temp file in same directory for atomic replace
        fd, tmp_path = tempfile.mkstemp(suffix='.yaml', dir=dest_dir)
        os.close(fd)
        try:
            _write_to(tmp_path)
            # create backup if requested
            if make_backup and os.path.exists(path):
                from datetime import datetime
                ts = datetime.now().strftime('%Y%m%d_%H%M%S')
                bak = f"{path}.bak.{ts}"
                shutil.copy2(path, bak)
            # atomic replace
            os.replace(tmp_path, path)
        except Exception:
            try:
                os.unlink(tmp_path)
            except Exception:
                pass
            raise
    else:
        # non-atomic direct write
        if make_backup and os.path.exists(path):
            from datetime import datetime
            ts = datetime.now().strftime('%Y%m%d_%H%M%S')
            bak = f"{path}.bak.{ts}"
            shutil.copy2(path, bak)
        _write_to(path)
