from functools import wraps

def name_decorator(param_name):
    def actual_decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for param in args[0].params:
                if param_name == param["NAME"]:
                    return param["VALUE"]
            #return func(*args, **kwargs)

        return wrapper
    return actual_decorator



class Block:

    def __init__(self, params):
        self.params = params

    @property
    @name_decorator("X0_L")
    def X0_L(self):
        pass

params = [
    
        {"NAME":"X1_L",
        "VALUE":42},
        {"NAME":"X0_L",
        "VALUE":53},
        {"NAME":"X2_L",
        "VALUE":76}
]

b = Block(params)
print(b.X0_L)