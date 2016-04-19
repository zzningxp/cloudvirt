import threading

class threads(object):
    def __init__(self, func_list=None): #, need_join=True):
        self.func_list = func_list
        self.threads = []
        self.need_join = True
        self.ret_dict = {}

    def set_func_list(self, func_list):
        self.func_list = func_list
    
    def set_need_join(self, need_join):
        self.need_join = need_join

    def start(self):
        self.thrs = []
        for i, func_tuple in enumerate(self.func_list):
            t = threading.Thread(target=self.trace_func, args=(i, ) + func_tuple)
            self.thrs.append(t)
 
        for thread_obj in self.thrs:
            thread_obj.start()

        if self.need_join:
            for thread_obj in self.thrs:
                thread_obj.join()
 
    def trace_func(self, index, func, *args, **kwargs):
        self.ret_dict[index] = func(*args, **kwargs)
    
    def get_return(self):
        return self.ret_dict
