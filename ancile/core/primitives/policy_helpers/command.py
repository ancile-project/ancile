

class Command:

    def __init__(self, command_name, params=None):
        self.command = command_name
        self.params = params

    def __repr__(self):
        if self.params:
            return f'{self.command}({", ".join(self.params)})'
        else:
            return f'{self.command}'
