#ifdef _DEBUG
#undef _DEBUG
#include <python.h>
#define _DEBUG
#else
#include <python.h>
#endif
#include <structmember.h>
#include "../diablo/diablo.h"
#include "../utilities/log.h"
#include "../api/api.h"

static PyObject *PyUnit_new(PyTypeObject *type, PyObject *args, PyObject *kwds) {
    PyUnit *self;
    self = (PyUnit *)type->tp_alloc(type, 0);
    return (PyObject *)self;
}

static PyMemberDef PyUnit_members[] = {
    {"id", T_UINT, offsetof(PyUnit, id), READONLY, ""},
    {"type", T_UINT, offsetof(PyUnit, type), READONLY, ""},
    {"dwTxtFileNo", T_UINT, offsetof(PyUnit, dwTxtFileNo), READONLY, ""},
    /* item */
    {"pItemPathdwPosX", T_USHORT, offsetof(PyUnit, pItemPathdwPosX), READONLY, ""},
    {"pItemPathdwPosY", T_USHORT, offsetof(PyUnit, pItemPathdwPosY), READONLY, ""},
    {"pItemDatadwQuality", T_USHORT, offsetof(PyUnit, pItemDatadwQuality), READONLY, ""},
    /* character */
    {"pPathxPos", T_USHORT, offsetof(PyUnit, pPathxPos), READONLY, ""},
    {"pPathyPos", T_USHORT, offsetof(PyUnit, pPathyPos), READONLY, ""},
    {NULL}
};

static PyTypeObject PyUnitType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "game.Unit",
    .tp_basicsize = sizeof(PyUnit),
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = PyUnit_new,
    .tp_members = PyUnit_members,
};

static PyObject *py_get_player_unit(PyObject *self, PyObject *args) {
    struct UnitAny *player = GetPlayerUnit();
    if (!player) Py_RETURN_NONE;

    PyUnit *py_unit = PyObject_New(PyUnit, &PyUnitType);
    py_unit->id = player->dwUnitId;
    py_unit->type = player->dwType;
    py_unit->unit = player;
    py_unit->pPathxPos = player->pPath->xPos;
    py_unit->pPathyPos = player->pPath->yPos;
    return (PyObject *)py_unit;
}

static PyObject *py_get_item_table(PyObject *self, PyObject *args) {
    PyObject *list = PyList_New(128);
    for (int i = 0; i < 128; i++) {
        struct UnitAny *unit = ItemTable[i];

        if (unit) {
            PyUnit *py_unit = (PyUnit *)PyObject_New(PyUnit, &PyUnitType);
            py_unit->id = unit->dwUnitId;
            py_unit->type = unit->dwType;
            py_unit->unit = unit;
            py_unit->dwTxtFileNo = unit->dwTxtFileNo;
            py_unit->pItemPathdwPosX = unit->pItemPath->dwPosX;
            py_unit->pItemPathdwPosY = unit->pItemPath->dwPosY;
            py_unit->pItemDatadwQuality = unit->pItemData->dwQuality;
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
    PickUp(unit_id, unit_type);
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
    PyThreadState *tstate = PyGILState_GetThisThreadState();

    if (!tstate || PyErr_Occurred()) {
        PyErr_Print();
        write_log("ERR", "Python thread state is invalid in python_tick().");
        PyGILState_Release(gstate);
        return;
    }

    Py_ssize_t size = PyList_Size(tick_functions);

    for (Py_ssize_t i = 0; i < size; i++) {
        PyObject *func = PyList_GetItem(tick_functions, i);
        if (func && PyCallable_Check(func)) {
            PyObject *result = PyObject_CallObject(func, NULL);
            if (!result) {
                PyErr_Print();
                PyErr_Clear();
                write_log("ERR", "Python tick function execution failed.");
            }
            Py_XDECREF(result);
        }
    }

    PyGILState_Release(gstate);
}

static PyObject *py_get_item_code(PyObject *self, PyObject *args) {
    uint32_t txt_file_no;
    if (!PyArg_ParseTuple(args, "I", &txt_file_no)) {
        return NULL;
    }

    struct UnitAny* pUnit = NULL;

    for (int i = 0; i < 128; i++) {
        if (ItemTable[i] && ItemTable[i]->dwTxtFileNo == txt_file_no) {
            pUnit = ItemTable[i];
            break;
        }
    }

    if (!pUnit) {
        Py_RETURN_NONE;
    }

    char itemCode[4] = {0};
    GetItemCodeEx(pUnit, itemCode);

    return PyUnicode_FromString(itemCode);
}

static PyObject *py_get_item_stats(PyObject *self, PyObject *args) {
    PyUnit *py_unit;
    if (!PyArg_ParseTuple(args, "O!", &PyUnitType, &py_unit)) {
        write_log("ERR", "Failed to parse PyUnit argument.");
        return NULL;
    }

    struct UnitAny *unit = py_unit->unit;
    if (!unit) {
        write_log("ERR", "Unit pointer is NULL in get_item_stats.");
        Py_RETURN_NONE;
    }

    if (!unit->pStats) {
        write_log("ERR", "Unit has no stats.");
        Py_RETURN_NONE;
    }

    struct StatList *statList = GetStatList(unit, NULL, 0x40);
    if (!statList) {
        write_log("ERR", "GetStatList returned NULL.");
        Py_RETURN_NONE;
    }

    struct Stat stats[256] = {0};
    uint32_t statCount = CopyStatList(statList, (struct Stat*)stats, 256);

    if (statCount == 0) {
        write_log("ERR", "CopyStatList returned 0 stats.");
        Py_RETURN_NONE;
    }

    PyObject *pyList = PyList_New(statCount);
    if (!pyList) {
        return NULL;
    }

    for (uint32_t i = 0; i < statCount; i++) {
        PyObject *pyTuple = PyTuple_New(3);
        if (!pyTuple) {
            Py_DECREF(pyList);
            return NULL;
        }

        PyTuple_SetItem(pyTuple, 0, PyLong_FromUnsignedLong(stats[i].wStatIndex));
        PyTuple_SetItem(pyTuple, 1, PyLong_FromUnsignedLong(stats[i].wSubIndex));
        PyTuple_SetItem(pyTuple, 2, PyLong_FromUnsignedLong(stats[i].dwStatValue));

        PyList_SetItem(pyList, i, pyTuple);
    }

    return pyList;
}

static PyObject *py_reveal_level(PyObject *self, PyObject *args) {
    struct UnitAny *unit = GetPlayerUnit();
    if (!unit || !unit->pPath || !unit->pPath->pRoom1 || !unit->pPath->pRoom1->pRoom2 || !unit->pPath->pRoom1->pRoom2->pLevel) {
        Py_RETURN_NONE;
    }
    reveal_act(unit->pAct->dwAct + 1);
    Py_RETURN_NONE;
}

static PyMethodDef GameMethods[] = {
    {"get_player_unit", py_get_player_unit, METH_NOARGS, NULL},
    {"get_item_table", py_get_item_table, METH_NOARGS, NULL},
    {"pick_up", py_interact, METH_VARARGS, NULL},
    {"write_log", py_write_log, METH_VARARGS, NULL},
    {"register_tick", py_register_tick, METH_VARARGS, NULL},
    {"get_item_code", py_get_item_code, METH_VARARGS, NULL},
    {"get_item_stats", py_get_item_stats, METH_VARARGS, NULL},
    {"reveal_level", py_reveal_level, METH_NOARGS, NULL},
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