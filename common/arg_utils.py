
def get_all_args(args):
    return GetAllArgs(args).run()


class GetAllArgs:
    def __init__(self, args: list[str]) -> None:
        self.ret = {}

        self.current_key = None
        self.current_positional_args = 0
        self.args = args

    def run(self):
        for arg in self.args:
            if self.is_key(arg):
                previous_key = self.current_key
                self.current_key = self.get_key(arg)
                if previous_key is not None:
                    self.ret[previous_key] = None
            else:
                self.add_value(arg)
                
        previous_key = self.current_key
        if previous_key is not None:
            self.ret[previous_key] = None
        return self.ret

    def is_key(self, string):
        return string.startswith("-")
    
    def get_key(self, string):
        return string.lstrip("-")

    def add_value(self, value):
        key = self.current_key
        if self.current_key is None:
            key = self.current_positional_args
            self.current_positional_args += 1
        self.current_key = None
        self.ret[key] = value

def get_paired_args_only(args):
    ret = {}
    iterator = iter(args)

    num_of_raw_arguments = 0
    try:
        while True:
            curr_args = next(iterator)
            num_of_raw_arguments += 1

            assert curr_args.startswith("-")
            key = curr_args.lstrip("-")

            value = next(iterator)            
            num_of_raw_arguments += 1
            ret[key] = value
    except StopIteration:
        if num_of_raw_arguments % 2 != 0:
            raise ValueError("An argument (key) has no pair value")
    return ret
