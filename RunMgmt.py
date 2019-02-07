from __future__ import print_function
import pickle
import os
p = os.path


class RunMgmt(object):
    """
    Run management for script development.

    The RunMgmt class helps to store and recover results that were previously
    computed. Usage like this:

    >>> with RunMgmt('OptionOne') as rm:
    >>>     if not rm.done:
    >>>         print('Doing OptionOne')
    >>>         rm.result = 'OptionOneResult'
    >>>     else:
    >>>         print('Loaded OptionOne: %s' % rm.result)
    """
    run_all = False
    silent = False
    folder = 'RunMgmt'

    def __init__(self, option):
        self.option  = option
        self.opt_path = p.join(self.folder, option)
        self.done = None
        self.result = None

    def __enter__(self):
        opt = self.option
        self.done = p.exists(self.opt_path)
        if self.done:
            with open(self.opt_path) as f:
                try:
                    self.result = pickle.load(f)
                except EnvironmentError:
                    print('RunMgmt: could not load result for <%s>' % opt)
                    self.done = False
        if not self.silent:
            if self.done:
                print('RunMgmt: loaded result for <%s>.' % opt)
            else:
                print('RunMgmt: starting <%s>' % opt)
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
    >>> @manage_run('my_option')
    >>> def do_work():
    >>>     print('working hard...')
    >>>     return 'hard-worked result'
    >>>
    >>> my_result = do_work()
    """
    def decorator(func):
        def wrapped_func(*args, **kws):
            with RunMgmt(option) as rm:
                if not rm.done:
                    rm.result = func(*args, **kws)
                return rm.result
        return  wrapped_func
    return decorator


if __name__ == '__main__':
    pass

#    RunMgmt.folder = 'RunMgmtTEST'
#
#    @manage_run('my_option')
#    def do_work():
#        print('working hard...')
#        return 'hard-worked result'
#
#    my_result = do_work()
#    print('result: ' + my_result)

#    with RunMgmt('OptionOne') as rm:
#        if not rm.done:
#            print('Doing OptionOne')
#            rm.result = 'OptionOneResult'
#        else:
#            print('Loaded OptionOne: %s' % rm.result)
