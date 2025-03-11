#ifdef _DEBUG
#undef _DEBUG
#include <python.h>
#define _DEBUG
#else
#include <python.h>
#endif
#include "../diablo/diablo.h"
#include "../utilities/log.h"
#include "../api/api.h"

typedef struct {
    PyObject_HEAD
    uint32_t id;
    uint32_t type;
    uint16_t x;
    uint16_t y;
} PyUnit;

static PyObject *PyUnit_new(PyTypeObject *type, PyObject *args, PyObject *kwds) {
    PyUnit *self;
    self = (PyUnit *)type->tp_alloc(type, 0);
    return (PyObject *)self;
}

static int PyUnit_init(PyUnit *self, PyObject *args, PyObject *kwds) {
    if (!PyArg_ParseTuple(args, "IHH", &self->id, &self->x, &self->y)) {
        return -1;
    }
    return 0;
}

static PyObject *PyUnit_repr(PyUnit *self) {
    return PyUnicode_FromFormat("<Unit id=%u, x=%u, y=%u>", self->id, self->x, self->y);
}

static PyTypeObject PyUnitType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "game.Unit",
    .tp_basicsize = sizeof(PyUnit),
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = PyUnit_new,
    .tp_init = (initproc)PyUnit_init,
    .tp_repr = (reprfunc)PyUnit_repr,
};

static PyObject *py_get_player_unit(PyObject *self, PyObject *args) {
    struct UnitAny *player = GetPlayerUnit();
    if (!player) Py_RETURN_NONE;

    PyUnit *py_unit = PyObject_New(PyUnit, &PyUnitType);
    py_unit->id = player->dwUnitId;
    py_unit->x = player->pPath->xPos;
    py_unit->y = player->pPath->yPos;
    return (PyObject *)py_unit;
}

static PyObject *py_get_item_table(PyObject *self, PyObject *args) {
    PyObject *list = PyList_New(128);
    for (int i = 0; i < 128; i++) {
        struct UnitAny *unit = ItemTable[i];
        if (unit) {
            PyUnit *py_unit = PyObject_New(PyUnit, &PyUnitType);
            py_unit->id = unit->dwUnitId;
            py_unit->x = unit->pItemPath->dwPosX;
            py_unit->y = unit->pItemPath->dwPosY;
            PyList_SET_ITEM(list, i, (PyObject *)py_unit);
        } else {
            PyList_SET_ITEM(list, i, Py_None);
            Py_INCREF(Py_None);
        }
    }
    return list;
}

static PyObject *py_interact(PyObject *self, PyObject *args) {
    uint32_t unit_id, unit_type;
    if (!PyArg_ParseTuple(args, "II", &unit_id, &unit_type)) {
        return NULL;
    }
    Interact(unit_id, unit_type);
    Py_RETURN_NONE;
}

static PyObject *py_write_log(PyObject *self, PyObject *args) {
    const char *level, *message;
    if (!PyArg_ParseTuple(args, "ss", &level, &message)) {
        return NULL;
    }
    write_log(level, "%s", message);
    Py_RETURN_NONE;
}

static PyObject *tick_functions = NULL;

static PyObject *py_register_tick(PyObject *self, PyObject *args) {
    PyObject *callback;
    if (!PyArg_ParseTuple(args, "O", &callback)) {
        return NULL;
    }
    if (!PyCallable_Check(callback)) {
        PyErr_SetString(PyExc_TypeError, "Argument must be callable");
        return NULL;
    }
    PyList_Append(tick_functions, callback);
    Py_RETURN_NONE;
}

void python_tick(void) {
    if (!tick_functions) return;
    PyGILState_STATE gstate = PyGILState_Ensure();
    Py_ssize_t size = PyList_Size(tick_functions);
    for (Py_ssize_t i = 0; i < size; i++) {
        PyObject *func = PyList_GetItem(tick_functions, i);
        if (func) {
            PyObject_CallObject(func, NULL);
        }
    }
    PyGILState_Release(gstate);
}

static PyMethodDef GameMethods[] = {
    {"get_player_unit", py_get_player_unit, METH_NOARGS, NULL},
    {"get_item_table", py_get_item_table, METH_NOARGS, NULL},
    {"interact", py_interact, METH_VARARGS, NULL},
    {"write_log", py_write_log, METH_VARARGS, NULL},
    {"register_tick", py_register_tick, METH_VARARGS, NULL},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef game_module = {
    PyModuleDef_HEAD_INIT, "game", NULL, -1, GameMethods
};

PyMODINIT_FUNC PyInit_game(void) {
    tick_functions = PyList_New(0);
    PyObject *module = PyModule_Create(&game_module);
    if (!module) return NULL;
    if (PyType_Ready(&PyUnitType) < 0) return NULL;
    Py_INCREF(&PyUnitType);
    PyModule_AddObject(module, "Unit", (PyObject *)&PyUnitType);
    return module;
}

void init_python(void) {
    Py_Initialize();
    PyImport_AppendInittab("game", PyInit_game);
    PyGILState_Ensure();
    PyRun_SimpleString("import game");
}