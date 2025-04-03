#ifdef _DEBUG
#undef _DEBUG
#include <python.h>
#define _DEBUG
#else
#include <python.h>
#endif

#include <structmember.h>
#include "../library.h"
#include "../diablo/diablo.h"
#include "../diablo/drawing.h"
#include "../utilities/list.h"
#include "../utilities/log.h"
#include "../api/api.h"

#include <windows.h>

#include "../diablo/hooks.h"

static PyObject *PyUnit_new(PyTypeObject *type, PyObject *args, PyObject *kwds) {
    PyUnit *self;
    self = (PyUnit *)type->tp_alloc(type, 0);
    return (PyObject *)self;
}

static PyMemberDef PyUnit_members[] = {
    {"id", T_UINT, offsetof(PyUnit, id), READONLY, ""},
    {"type", T_UINT, offsetof(PyUnit, type), READONLY, ""},
    {"dwTxtFileNo", T_UINT, offsetof(PyUnit, dwTxtFileNo), READONLY, ""},
    {"dwMode", T_UINT, offsetof(PyUnit, dwMode), READONLY, ""},
    /* item */
    {"pItemDatadwFlags", T_UINT, offsetof(PyUnit, pItemDatadwFlags), READONLY, ""},
    {"pItemDatadwItemLevel", T_UINT, offsetof(PyUnit, pItemDatadwItemLevel), READONLY, ""},
    {"pItemDatadpOwner", T_UINT, offsetof(PyUnit, pItemDatadpOwner), READONLY, ""},
    {"pItemPathdwPosX", T_USHORT, offsetof(PyUnit, pItemPathdwPosX), READONLY, ""},
    {"pItemPathdwPosY", T_USHORT, offsetof(PyUnit, pItemPathdwPosY), READONLY, ""},
    {"pItemDatadwQuality", T_USHORT, offsetof(PyUnit, pItemDatadwQuality), READONLY, ""},
    /* character */
    {"pPathxPos", T_USHORT, offsetof(PyUnit, pPathxPos), READONLY, ""},
    {"pPathyPos", T_USHORT, offsetof(PyUnit, pPathyPos), READONLY, ""},
    {"dwAct", T_UINT, offsetof(PyUnit, dwAct), READONLY, ""},
    /* monster */
    {"pMonsterDatawName", T_UINT, offsetof(PyUnit, pMonsterDatawName), READONLY, ""},
    {"pMonsterDatawUniqueNo", T_USHORT, offsetof(PyUnit, pMonsterDatawUniqueNo), READONLY, ""},
    {"pMonsterDatafNormal", T_BOOL, offsetof(PyUnit, pMonsterDatafNormal), READONLY, ""},
    {"pMonsterDatafChamp", T_BOOL, offsetof(PyUnit, pMonsterDatafChamp), READONLY, ""},
    {"pMonsterDatafBoss", T_BOOL, offsetof(PyUnit, pMonsterDatafBoss), READONLY, ""},
    {"pMonsterDatafMinion", T_BOOL, offsetof(PyUnit, pMonsterDatafMinion), READONLY, ""},
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

static PyObject *build_player_unit(struct UnitAny *player) {
    if (!player) Py_RETURN_NONE;

    PyUnit *py_unit = PyObject_New(PyUnit, &PyUnitType);
    py_unit->id = player->dwUnitId;
    py_unit->type = player->dwType;
    py_unit->unit = player;
    if (player->pPath) {
        py_unit->pPathxPos = player->pPath->xPos;
        py_unit->pPathyPos = player->pPath->yPos;
    } else {
        py_unit->pPathxPos = 0;
        py_unit->pPathyPos = 0;
    }
    py_unit->dwAct = player->dwAct;
    return (PyObject *)py_unit;
}

static PyObject *py_get_player_unit(PyObject *self, PyObject *args) {
    struct UnitAny *player = GetPlayerUnit();
    return build_player_unit(player);
}

static PyObject *build_item_unit(struct UnitAny *item) {
    PyUnit *py_unit = PyObject_New(PyUnit, &PyUnitType);
    py_unit->id = item->dwUnitId;
    py_unit->type = item->dwType;
    py_unit->unit = item;
    py_unit->dwTxtFileNo = item->dwTxtFileNo;
    py_unit->pItemDatadwFlags = item->pItemData->dwFlags;
    py_unit->pItemDatadwItemLevel = item->pItemData->dwItemLevel;
    py_unit->pItemDatadpOwner = item->pItemData->pOwnerInventory ? item->pItemData->pOwnerInventory->pOwner : NULL;
    py_unit->pItemPathdwPosX = item->pItemPath->dwPosX;
    py_unit->pItemPathdwPosY = item->pItemPath->dwPosY;
    py_unit->pItemDatadwQuality = item->pItemData->dwQuality;
    return (PyObject *)py_unit;
}

static PyObject *build_monster_unit(struct UnitAny *monster) {
    if (!monster) Py_RETURN_NONE;

    PyUnit *py_unit = PyObject_New(PyUnit, &PyUnitType);
    py_unit->unit = monster;
    py_unit->id = monster->dwUnitId;
    py_unit->type = monster->dwType;
    py_unit->dwMode = monster->dwMode;
    py_unit->dwTxtFileNo = monster->dwTxtFileNo;
    if (monster->pPath) {
        py_unit->pPathxPos = monster->pPath->xPos;
        py_unit->pPathyPos = monster->pPath->yPos;
    } else {
        py_unit->pPathxPos = 0;
        py_unit->pPathyPos = 0;
    }
    py_unit->pMonsterDatawName = monster->pMonsterData ? monster->pMonsterData->wName : NULL;
    py_unit->pMonsterDatawUniqueNo = monster->pMonsterData->wUniqueNo;
    py_unit->pMonsterDatafNormal = (monster->pMonsterData->fNormal & 1) == 1;
    py_unit->pMonsterDatafChamp = (monster->pMonsterData->fChamp & 1) == 1;
    py_unit->pMonsterDatafBoss = (monster->pMonsterData->fBoss & 1) == 1;
    py_unit->pMonsterDatafMinion = (monster->pMonsterData->fMinion & 1) == 1;
    return (PyObject *)py_unit;
}

static PyObject *py_get_item_table(PyObject *self, PyObject *args) {
    PyObject *list = PyList_New(128);
    for (int i = 0; i < 128; i++) {
        struct UnitAny *unit = ItemTable[i];

        if (unit) {
            PyObject *item = build_item_unit(unit);
            PyList_SET_ITEM(list, i, item);
        } else {
            Py_INCREF(Py_None);
            PyList_SET_ITEM(list, i, Py_None);
        }
    }
    return list;
}

static PyObject *py_get_nearby_monsters(PyObject *self, PyObject *args) {
    struct UnitAny *player = GetPlayerUnit();
    PyObject *list = PyList_New(128);

    for (struct Room1* room1 = player->pAct->pRoom1; room1; room1 = room1->pRoomNext) {
        for (struct UnitAny* unit = room1->pUnitFirst; unit; unit = unit->pListNext) {
            PyObject *monster = build_monster_unit(unit);
            PyList_Append(list, monster);
        }
    }

    return list;
}

static PyObject *py_get_monster_table(PyObject *self, PyObject *args) {
    PyObject *list = PyList_New(128);
    for (int i = 0; i < 128; i++) {
        struct UnitAny *unit = MonsterTable[i];

        if (unit) {
            PyObject *item = build_monster_unit(unit);
            PyList_SET_ITEM(list, i, item);
        } else {
            Py_INCREF(Py_None);
            PyList_SET_ITEM(list, i, Py_None);
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

static PyObject *flex_loop_functions = NULL;
static PyObject *draw_automap_functions = NULL;

static PyObject *py_register_flex_loop(PyObject *self, PyObject *args) {
    PyObject *callback;
    if (!PyArg_ParseTuple(args, "O", &callback)) {
        return NULL;
    }
    if (!PyCallable_Check(callback)) {
        PyErr_SetString(PyExc_TypeError, "Argument must be callable");
        return NULL;
    }
    PyList_Append(flex_loop_functions, callback);
    Py_RETURN_NONE;
}

static PyObject *py_register_draw_automap_loop(PyObject *self, PyObject *args) {
    PyObject *callback;
    if (!PyArg_ParseTuple(args, "O", &callback)) {
        return NULL;
    }
    if (!PyCallable_Check(callback)) {
        PyErr_SetString(PyExc_TypeError, "Argument must be callable");
        return NULL;
    }
    PyList_Append(draw_automap_functions, callback);
    Py_RETURN_NONE;
}

void flex_loop(void) {
    if (!flex_loop_functions) {
        return;
    }

    PyGILState_STATE gstate = PyGILState_Ensure();
    PyThreadState *tstate = PyGILState_GetThisThreadState();

    if (!tstate || PyErr_Occurred()) {
        PyErr_Print();
        write_log("ERR", "Invalid Python thread state in flex_loop");
        PyGILState_Release(gstate);
        return;
    }

    Py_ssize_t size = PyList_Size(flex_loop_functions);

    for (Py_ssize_t i = 0; i < size; i++) {
        PyObject *func = PyList_GetItem(flex_loop_functions, i);
        if (func && PyCallable_Check(func)) {
            PyObject *result = PyObject_CallObject(func, NULL);
            if (!result) {
                PyErr_Print();
                write_log("ERR", "Python tick function %zd failed", i);
            }
            Py_XDECREF(result);
        } else {
            write_log("WRN", "flex_loop_functions[%zd] is not callable or NULL", i);
        }
    }

    PyGILState_Release(gstate);
}

void automap_loop(void) {
    if (!draw_automap_functions) {
        return;
    }

    PyGILState_STATE gstate = PyGILState_Ensure();
    PyThreadState *tstate = PyGILState_GetThisThreadState();

    if (!tstate || PyErr_Occurred()) {
        PyErr_Print();
        write_log("ERR", "Invalid Python thread state in automap_loop");
        PyGILState_Release(gstate);
        return;
    }

    Py_ssize_t num_funcs = PyList_Size(draw_automap_functions);

    EnterCriticalSection(&plugins_lock);
    struct List *plugin_node = plugins;

    while (plugin_node) {
        struct Plugin *plugin = plugin_node->data;
        struct List *new_list = NULL;

        for (Py_ssize_t i = 0; i < num_funcs; ++i) {
            PyObject *func = PyList_GetItem(draw_automap_functions, i);
            if (func && PyCallable_Check(func)) {
                PyObject *result = PyObject_CallObject(func, NULL);
                if (!result) {
                    PyErr_Print();
                    write_log("ERR", "Automap function %zd call failed", i);
                    continue;
                }

                if (PyList_Check(result)) {
                    Py_ssize_t n = PyList_Size(result);
                    for (Py_ssize_t j = 0; j < n; ++j) {
                        PyObject *item = PyList_GetItem(result, j);
                        if (!item || !PyObject_HasAttrString(item, "_to_dict")) continue;

                        PyObject *dict = PyObject_CallMethod(item, "_to_dict", NULL);
                        if (!dict || !PyDict_Check(dict)) {
                            Py_XDECREF(dict);
                            continue;
                        }

                        struct Element *el = malloc(sizeof(struct Element));
                        if (!el) {
                            Py_DECREF(dict);
                            continue;
                        }

                        memset(el, 0, sizeof(struct Element));

                        PyObject *type_obj = PyObject_GetAttrString(item, "__class__");
                        if (type_obj) {
                            PyObject *name = PyObject_GetAttrString(type_obj, "__name__");
                            if (PyUnicode_Check(name)) {
                                if (PyUnicode_CompareWithASCIIString(name, "TextElement") == 0) el->type = TEXT_ELEMENT;
                                else if (PyUnicode_CompareWithASCIIString(name, "LineElement") == 0) el->type = LINE_ELEMENT;
                                else if (PyUnicode_CompareWithASCIIString(name, "CrossElement") == 0) el->type = CROSS_ELEMENT;
                                else el->type = 0xFF;
                            }
                            Py_XDECREF(name);
                        }
                        Py_XDECREF(type_obj);

                        PyObject *text = PyDict_GetItemString(dict, "text");
                        if (text && PyUnicode_Check(text)) {
                            strncpy(el->text, PyUnicode_AsUTF8(text), sizeof(el->text) - 1);
                            el->text[sizeof(el->text) - 1] = '\0';
                        }

                        PyObject *color = PyDict_GetItemString(dict, "color");
                        if (color && PyLong_Check(color)) {
                            el->color = (uint8_t)PyLong_AsLong(color);
                        }

                        PyObject *x1 = PyDict_GetItemString(dict, "x1");
                        PyObject *y1 = PyDict_GetItemString(dict, "y1");
                        PyObject *x2 = PyDict_GetItemString(dict, "x2");
                        PyObject *y2 = PyDict_GetItemString(dict, "y2");

                        if (x1 && PyLong_Check(x1)) el->x1 = (uint32_t)PyLong_AsUnsignedLong(x1);
                        if (y1 && PyLong_Check(y1)) el->y1 = (uint32_t)PyLong_AsUnsignedLong(y1);
                        if (x2 && PyLong_Check(x2)) el->x2 = (uint32_t)PyLong_AsUnsignedLong(x2);
                        if (y2 && PyLong_Check(y2)) el->y2 = (uint32_t)PyLong_AsUnsignedLong(y2);

                        list_insert(&new_list, el);
                        Py_DECREF(dict);
                    }
                }
                Py_DECREF(result);
            } else {
                write_log("WRN", "draw_automap_functions[%zd] is not callable or NULL", i);
            }
        }

        if (plugin->automap_elements) {
            list_destroy(&plugin->automap_elements);
        }

        plugin->automap_elements = new_list;
        plugin_node = plugin_node->next;
    }

    LeaveCriticalSection(&plugins_lock);
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

    struct StatList *statList = unit->pStats; //GetStatList(unit, NULL, 0x40);
    if (!statList) {
        write_log("ERR", "GetStatList returned NULL.");
        Py_RETURN_NONE;
    }

    struct Stat* stats = statList->StatVec.pStats;
    uint32_t statCount = statList->StatVec.wCount;

    // struct Stat stats[256] = {0};
    // uint32_t statCount = CopyStatList(statList, (struct Stat*)stats, 256);
    //
    // if (statCount == 0) {
    //     write_log("ERR", "CopyStatList returned 0 stats.");
    //     Py_RETURN_NONE;
    // }

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

static PyObject *py_reveal_automap(PyObject *self, PyObject *args) {
    struct UnitAny *unit = GetPlayerUnit();
    if (!unit || !unit->pPath || !unit->pPath->pRoom1 || !unit->pPath->pRoom1->pRoom2 || !unit->pPath->pRoom1->pRoom2->pLevel) {
        Py_RETURN_NONE;
    }
    for (int i = 1; i <= 5; i++) {
        reveal_act(i);
    }
    Py_RETURN_NONE;
}

static PyMemberDef PyGameInfo_members[] = {
    {"name", T_STRING, offsetof(PyGameInfo, name), READONLY, ""},
    {"password", T_STRING, offsetof(PyGameInfo, password), READONLY, ""},
    {"server_ip", T_STRING, offsetof(PyGameInfo, server_ip), READONLY, ""},
    {"account_name", T_STRING, offsetof(PyGameInfo, account_name), READONLY, ""},
    {"character_name", T_STRING, offsetof(PyGameInfo, character_name), READONLY, ""},
    {"realm_name", T_STRING, offsetof(PyGameInfo, realm_name), READONLY, ""},
    {NULL}
};

static PyTypeObject PyGameInfoType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "game.GameInfo",
    .tp_basicsize = sizeof(PyGameInfo),
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_members = PyGameInfo_members,
};

static PyObject *build_game_info(struct GameInfo *game_info) {
    if (!game_info) Py_RETURN_NONE;

    PyGameInfo *py_game_info = PyObject_New(PyGameInfo, &PyGameInfoType);
    py_game_info->account_name = game_info->szAccountName;
    py_game_info->character_name = game_info->szCharName;
    py_game_info->name = game_info->szGameName;
    py_game_info->password = game_info->szGamePassword;
    py_game_info->realm_name = game_info->szRealmName;
    py_game_info->server_ip = game_info->szGameServerIp;

    return (PyObject *)py_game_info;
}

static PyObject *py_get_game_info(PyObject *self, PyObject *args) {
    if (!game_info || !*game_info) {
        Py_RETURN_NONE;
    }
    return build_game_info(*game_info);
}

static PyObject *py_is_game_ready(PyObject *self, PyObject *args) {
	struct UnitAny* player = GetPlayerUnit();
    if (player != NULL &&
        player->pPath != NULL &&
        player->pPath->pRoom1 != NULL &&
        player->pPath->pRoom1->pRoom2 != NULL &&
        player->pPath->pRoom1->pRoom2->pLevel != NULL &&
        player->pPath->pRoom1->pRoom2->pLevel->dwLevelNo > 0 &&
        player->pAct != NULL &&
        player->pAct->pRoom1 != NULL &&
        player->pInventory != NULL &&
        player->pPath->xPos > 0 &&
        player->pPath->yPos > 0) {
        Py_RETURN_TRUE;
    } else {
        Py_RETURN_FALSE;
    }
}

static PyObject *py_build_player_unit_from_ptr(PyObject *self, PyObject *args) {
    uint64_t addr;
    if (!PyArg_ParseTuple(args, "K", &addr))
        return NULL;
    return build_player_unit((struct UnitAny *)addr);
}

static PyObject *py_wstring_at(PyObject *self, PyObject *args) {
    const wchar_t *addr;
    if (!PyArg_ParseTuple(args, "k", &addr))  // Use "k" for unsigned long (pointer-sized)
        return NULL;

    if (!addr)
        Py_RETURN_NONE;

    return PyUnicode_FromWideChar(addr, -1);
}

static PyObject *py_print_game_string(PyObject *self, PyObject *args) {
    const char *message;
    int color;

    if (!PyArg_ParseTuple(args, "si", &message, &color)) {
        return NULL;
    }

    int len = MultiByteToWideChar(CP_UTF8, 0, message, -1, NULL, 0);
    if (len == 0) {
        PyErr_SetString(PyExc_ValueError, "Failed to convert message to wide string.");
        return NULL;
    }

    wchar_t *wMessage = (wchar_t *)malloc(len * sizeof(wchar_t));
    if (!wMessage) {
        PyErr_NoMemory();
        return NULL;
    }

    MultiByteToWideChar(CP_UTF8, 0, message, -1, wMessage, len);

    if (PrintGameString) {
        PrintGameString(wMessage, color);
    } else {
        write_log("ERR", "PrintGameString is NULL");
    }

    free(wMessage);
    Py_RETURN_NONE;
}

static PyMethodDef GameMethods[] = {
    {"get_game_info", py_get_game_info, METH_NOARGS, NULL},
    {"is_game_ready", py_is_game_ready, METH_NOARGS, NULL},
    {"get_player_unit", py_get_player_unit, METH_NOARGS, NULL},
    {"get_item_table", py_get_item_table, METH_NOARGS, NULL},
    {"get_monster_table", py_get_monster_table, METH_NOARGS, NULL},
    {"get_nearby_monsters", py_get_nearby_monsters, METH_NOARGS, NULL},
    {"pick_up", py_interact, METH_VARARGS, NULL},
    {"write_log", py_write_log, METH_VARARGS, NULL},
    {"register_flex_loop", py_register_flex_loop, METH_VARARGS, NULL},
    {"register_draw_automap_loop", py_register_draw_automap_loop, METH_VARARGS, NULL},
    {"get_item_code", py_get_item_code, METH_VARARGS, NULL},
    {"get_item_stats", py_get_item_stats, METH_VARARGS, NULL},
    {"reveal_automap", py_reveal_automap, METH_NOARGS, NULL},
    {"build_player_unit_from_ptr", py_build_player_unit_from_ptr, METH_VARARGS, NULL},
    {"wstring_at", py_wstring_at, METH_VARARGS, NULL},
    {"print_game_string", py_print_game_string, METH_VARARGS, NULL},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef game_module = {
    PyModuleDef_HEAD_INIT, "game", NULL, -1, GameMethods
};

PyMODINIT_FUNC PyInit_game(void) {
    flex_loop_functions = PyList_New(0);

    draw_automap_functions = PyList_New(0);

    PyObject *module = PyModule_Create(&game_module);
    if (!module) {
        write_log("ERR", "Failed to create game module");
        return NULL;
    }

    if (PyType_Ready(&PyUnitType) < 0) {
        write_log("ERR", "PyUnitType not ready");
        return NULL;
    }
    Py_INCREF(&PyUnitType);
    PyModule_AddObject(module, "Unit", (PyObject *)&PyUnitType);

    if (PyType_Ready(&PyGameInfoType) < 0) {
        write_log("ERR", "PyGameInfoType not ready");
        return NULL;
    }
    Py_INCREF(&PyGameInfoType);
    PyModule_AddObject(module, "GameInfo", (PyObject *)&PyGameInfoType);

    return module;
}
