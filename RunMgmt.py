from __future__ import print_function
import pickle
import os
p = os.path

bypass_mgmt = True


class RunMgmt(object):
    """
    Run management for script development.

    The RunMgmt class helps to store and recover results that were previously
    computed. Usage like this:

    #>>> with RunMgmt('OptionOne') as rm:
    #>>>     if not rm.done:
    #>>>         print('Doing OptionOne')
    #>>>         rm.result = 'OptionOneResult'
    #>>>     else:
    #>>>         print('Loaded OptionOne: %s' % rm.result)
    """
    silent = False
    folder = 'RunMgmt'

    def __init__(self, option):
        self.option  = option
        self.opt_path = p.join(self.folder, option)
        self.done = None
        self.result = None
        self.catch_on_load = Exception  # EnvironmentError

    def __enter__(self):
        opt = self.option
        self.done = p.exists(self.opt_path)
        if self.done:
            with open(self.opt_path) as f:
                try:
                    self.result = pickle.load(f)
                except self.catch_on_load:
                    print('RunMgmt: could not load result for "%s"' % opt)
                    self.done = False
        if not self.silent:
            if self.done:
                print('RunMgmt: loaded result for "%s".' % opt)
            else:
                print('RunMgmt: starting "%s"' % opt)
        return self

    def __exit__(self, type, value, traceback):
        if not p.exists(self.folder):
            os.makedirs(self.folder)
        with open(self.opt_path, 'w') as f:
            pickle.dump(self.result, f)


def manage_run(option):
    """
    Same as above with with a callback function to produce the result.

    Usage:
    #>>> @manage_run('my_option')
    #>>> def do_work():
    #>>>     print('working hard...')
    #>>>     return 'hard-worked result'
    #>>>
    #>>> my_result = do_work()
    """
    def decorator(func):
        if bypass_mgmt:
            return func
        def wrapped_func(*args, **kws):
            with RunMgmt(option) as rm:
                if not rm.done:
                    rm.result = func(*args, **kws)
                return rm.result
        return  wrapped_func
    return decorator


class Cache(dict):
    """
    Disk-synchronised cache.

    Use get(key, default) for loading and normal item-setting for storing
    from/to disk. Items are _not_ loaded on Cache instanciation. Erase items by
    deleting them from disk (by hand).

    >>> c = Cache('RunMgmtTest')    # sync to 'RunMgmtTest' folder
    >>> c.get('hello')              # will try to load
    >>> c['hello'] = 'World'
    \x1B[33mCache: stored value for "hello"\x1B[0m
    >>> c.get('hello')              # will not load if present
    'World'
    >>>
    >>> c = Cache('RunMgmtTest')    # re-instantiate
    >>> res = c.get('hello')        # will load
    \x1B[33mCache: loaded value for "hello"\x1B[0m
    >>> res
    'World'
    >>> import shutil; shutil.rmtree('RunMgmtTest')
    """

    catch_on_load = Exception  # EnvironmentError

    def __init__(self, folder):
        super(Cache, self).__init__()
        self.folder = folder

    def print(self, msg):
        print('\x1B[33m'+msg+'\x1B[0m')

    def get(self, k, default=None):
        v = super(Cache, self).get(k, default)
        if isinstance(v, type(None)):
            v_path = p.join(self.folder, k)
            if p.exists(v_path):
                with open(v_path) as f:
                    try:
                        v = pickle.load(f)
                        super(Cache, self).__setitem__(k, v)
                        self.print('Cache: loaded value for "%s"' % k)
                    except self.catch_on_load as e:
                        self.print('Cache: could not load value for "%s"' % k)
                        self.print('Cache: exception: %s' % e)
        return v

    def __setitem__(self, k, v):
        if not p.exists(self.folder):
            os.makedirs(self.folder)
        v_path = p.join(self.folder, k)
        with open(v_path, 'w') as f:
            pickle.dump(v, f)
        self.print('Cache: stored value for "%s"' % k)
        super(Cache, self).__setitem__(k, v)

    # __delitem__(self, k):
    #     pass

    # __contains__(self, k):
    #     pass


if __name__ == '__main__':
#    pass
    import doctest
    doctest.testmod()

#    c = Cache('RunMgmtTest')
#    c.get('hello')
#    c['hello'] = 'World'

#    RunMgmt.folder = 'RunMgmtTEST'
#    @manage_run('my_option')
#    def do_work():
#        print('working hard...')
#        return 'hard-worked result'
#    my_result = do_work()
#    print('result: ' + my_result)

#    with RunMgmt('OptionOne') as rm:
#        if not rm.done:
#            print('Doing OptionOne')
#            rm.result = 'OptionOneResult'
#        else:
#            print('Loaded OptionOne: %s' % rm.result)
