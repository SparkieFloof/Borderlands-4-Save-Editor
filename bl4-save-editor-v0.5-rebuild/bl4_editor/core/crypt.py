import subprocess

class CryptWrapper:
    def __init__(self, exe_path='bl4-crypt-cli.exe', logger=None):
        self.exe_path = exe_path
        self.logger = logger

    def decrypt(self, input_file, output_file, userid=None):
        args = [self.exe_path, 'decrypt', '-i', str(input_file), '-o', str(output_file)]
        if userid:
            args.extend(['-u', str(userid)])
        if self.logger:
            self.logger.debug(f'[Crypt] Args: {args}', category='Crypt')
        try:
            proc = subprocess.run(args, capture_output=True, text=True)
        except FileNotFoundError as e:
            if self.logger: self.logger.error(f'Crypt executable not found: {e}', category='Crypt')
            return False
        if proc.returncode != 0:
            if self.logger: self.logger.error(proc.stderr.strip(), category='Crypt')
            return False
        if self.logger and proc.stdout.strip():
            self.logger.debug(proc.stdout.strip(), category='Crypt')
        return True

    def encrypt(self, input_file, output_file, userid=None):
        args = [self.exe_path, 'encrypt', '-i', str(input_file), '-o', str(output_file)]
        if userid:
            args.extend(['-u', str(userid)])
        if self.logger:
            self.logger.debug(f'[Crypt] Args: {args}', category='Crypt')
        try:
            proc = subprocess.run(args, capture_output=True, text=True)
        except FileNotFoundError as e:
            if self.logger: self.logger.error(f'Crypt executable not found: {e}', category='Crypt')
            return False
        if proc.returncode != 0:
            if self.logger: self.logger.error(proc.stderr.strip(), category='Crypt')
            return False
        if self.logger and proc.stdout.strip():
            self.logger.debug(proc.stdout.strip(), category='Crypt')
        return True
