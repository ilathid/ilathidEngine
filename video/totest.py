import time
import ctypes

def _get_argc_argv():
    argv = ctypes.POINTER(ctypes.POINTER(ctypes.c_char))()
    argc = ctypes.c_int()
    ctypes.pythonapi.Py_GetArgcArgv(ctypes.byref(argc), ctypes.byref(argv))
    return argc, argv

def _set_first_argv(name):
    name = str(name)

    libc = ctypes.CDLL(None)
    strlen = libc.strlen
    strlen.argtypes = [ctypes.c_void_p]
    strlen.restype = ctypes.c_size_t

    memset = libc.memset
    memset.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_size_t]
    memset.restype = ctypes.c_void_p

    argc, argv = _get_argc_argv()
    libc.strncpy(argv[0], name, len(name))
    next_name = ctypes.addressof(argv[0].contents) + len(name)
    next_len = strlen(next_name)
    libc.memset(next_name, 0, next_len)


# Change process name
libc = ctypes.cdll.LoadLibrary('libc.so.7')
_set_first_argv("totest_python");
libc.setproctitle("totest_python")

mydll = ctypes.CDLL("./libMPPool.so.1.0")

mydll.mixer_init()
mydll.mixer_new_class("sfx")
mydll.mixer_set_volume("sfx", 200)
# mp = mydll.MPP_create("./test.ogg", 0, "sfx", 0)
mp = mydll.MPP_create("./small.ogv", 0, "sfx", 0)
mydll.MPP_play(mp)
time.sleep(16)

