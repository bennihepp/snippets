#include <Python.h>

static PyObject *ExtError;

static PyObject *
ext_system(PyObject *self, PyObject *args)
{
    const char *command;
    int sts;

    if (!PyArg_ParseTuple(args, "s", &command))
        return NULL;
    sts = system(command);
    if (sts < 0) {
        PyErr_SetString(ExtError, "System command failed");
        return NULL;
    }
    else if (sts > 0) {
        PyErr_SetString(ExtError, "Command failed");
        return NULL;
    }
    return PyLong_FromLong(sts);
    /*return Py_BuildValue("i", sts);*/
}

static PyObject *ext_callback = NULL;

static PyObject *
ext_set_callback(PyObject *self, PyObject *args)
{
    PyObject *result = NULL;
    PyObject *temp;

    if (PyArg_ParseTuple(args, "O:set_callback", &temp)) {
        if (!PyCallable_Check(temp)) {
            PyErr_SetString(PyExc_TypeError, "parameter must be callable");
            return NULL;
        }
        Py_XINCREF(temp);         /* Add a reference to new callback */
        Py_XDECREF(ext_callback);  /* Dispose of previous callback */
        ext_callback = temp;       /* Remember new callback */
        /* Boilerplate to return "None" */
        Py_INCREF(Py_None);
        result = Py_None;
    }
    return result;
}

static PyObject *
ext_run(PyObject *self, PyObject *args)
{
    int arg1, arg2;
    PyObject *arglist;
    PyObject *result;
    PyObject *pstr;
    const char *cstr;

    arg1 = 123;
    arg2 = 987;

    /* Time to call the callback */
    arglist = Py_BuildValue("(ii)", arg1, arg2);
    if (arglist == NULL)
        return NULL;
    result = PyObject_CallObject(ext_callback, arglist);
    Py_DECREF(arglist);
    if (result == NULL) {
        return NULL;
    }
    pstr = PyObject_Str(result);
    if (pstr == NULL) {
        Py_DECREF(result);
        return NULL;
    }
    cstr = PyString_AsString(pstr);
    if (cstr == NULL) {
        Py_DECREF(pstr);
        return NULL;
    }
    Py_DECREF(pstr);
    printf("callback returned: %s\n", cstr);
    return result;
}

static PyMethodDef ExtMethods[] = {
    {"system", ext_system, METH_VARARGS,
     "Execute a shell command."},
    {"run", ext_run, METH_VARARGS,
     "Run."},
    {"set_callback", ext_set_callback, METH_VARARGS,
     "Set callback."},
    {NULL, NULL, 0, NULL}
};

PyMODINIT_FUNC
initext(void)
{
    PyObject *m;

    printf("initexec()\n");
    m = Py_InitModule("ext", ExtMethods);
    if (m == NULL)
        return ;

    ExtError = PyErr_NewException("ext.error", NULL, NULL);
    Py_INCREF(ExtError);
    PyModule_AddObject(m, "error", ExtError);
}


