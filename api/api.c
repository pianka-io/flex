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
#include "../diablo/constants.h"
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
    py_unit->dwMode = player->dwMode;
    if (player->pPath) {
        py_unit->pPathxPos = player->pPath->xPos;
        py_unit->pPathyPos = player->pPath->yPos;
    } else {
        py_unit->pPathxPos = 0;
        py_unit->pPathyPos = 0;
    }
    py_unit->dwAct = player->dwAct;
    py_unit->pAct = player->pAct;
    return (PyObject *)py_unit;
}

static PyObject *py_get_player_unit(PyObject *self, PyObject *args) {
    __try {
        struct UnitAny *player = GetPlayerUnit();
        return build_player_unit(player);
    } __except(EXCEPTION_EXECUTE_HANDLER) {
        write_log("ERR", "crash in py_get_player_unit");
        Py_RETURN_NONE;
    }
}

static PyObject *build_item_unit(struct UnitAny *item) {
    PyUnit *py_unit = PyObject_New(PyUnit, &PyUnitType);
    py_unit->id = item->dwUnitId;
    py_unit->type = item->dwType;
    py_unit->unit = item;
    py_unit->dwMode = item->dwMode;
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
    __try {
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
    } __except(EXCEPTION_EXECUTE_HANDLER) {
        write_log("ERR", "crash in py_get_item_table");
        Py_RETURN_NONE;
    }
}

static PyObject *py_get_nearby_monsters(PyObject *self, PyObject *args) {
    __try {
        struct UnitAny *player = GetPlayerUnit();
        PyObject *list = PyList_New(128);

        for (struct Room1* room1 = player->pAct->pRoom1; room1; room1 = room1->pRoomNext) {
            for (struct UnitAny* unit = room1->pUnitFirst; unit; unit = unit->pListNext) {
                PyObject *monster = build_monster_unit(unit);
                PyList_Append(list, monster);
            }
        }

        return list;
    } __except(EXCEPTION_EXECUTE_HANDLER) {
        write_log("ERR", "crash in py_get_nearby_monsters");
        Py_RETURN_NONE;
    }
}

static PyObject *py_get_monster_table(PyObject *self, PyObject *args) {
    __try {
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
    } __except(EXCEPTION_EXECUTE_HANDLER) {
        write_log("ERR", "crash in py_get_monster_table");
        Py_RETURN_NONE;
    }
}

static PyObject *py_interact(PyObject *self, PyObject *args) {
    __try {
        uint32_t unit_id, unit_type;
        if (!PyArg_ParseTuple(args, "II", &unit_id, &unit_type)) {
            return NULL;
        }
        send_pick_up_item(unit_id, unit_type);
        Py_RETURN_NONE;
    } __except(EXCEPTION_EXECUTE_HANDLER) {
        write_log("ERR", "crash in py_interact");
        Py_RETURN_NONE;
    }
}

static PyObject *py_write_log(PyObject *self, PyObject *args) {
    __try {
        const char *level, *message;
        if (!PyArg_ParseTuple(args, "ss", &level, &message)) {
            return NULL;
        }
        write_log(level, "%s", message);
        Py_RETURN_NONE;
    } __except(EXCEPTION_EXECUTE_HANDLER) {
        write_log("ERR", "crash in py_write_log");
        Py_RETURN_NONE;
    }
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

    EnterCriticalSection(&plugins_lock);

    Py_ssize_t num_funcs = PyList_Size(draw_automap_functions);
    if (global_automap_elements) {
        list_destroy(&global_automap_elements);
    }
    global_automap_elements = NULL;

    struct List *new_list = NULL;

    for (Py_ssize_t i = 0; i < num_funcs; ++i) {
        PyObject *func = PyList_GetItem(draw_automap_functions, i);
        if (!func || !PyCallable_Check(func)) continue;

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
    }

    global_automap_elements = new_list;
    LeaveCriticalSection(&plugins_lock);
    PyGILState_Release(gstate);
}

static PyObject *py_get_item_code(PyObject *self, PyObject *args) {
    __try {
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
        get_item_code(pUnit, itemCode);

        return PyUnicode_FromString(itemCode);
    } __except(EXCEPTION_EXECUTE_HANDLER) {
        write_log("ERR", "crash in py_get_item_code");
        Py_RETURN_NONE;
    }
}

static PyObject *py_get_item_stats(PyObject *self, PyObject *args) {
    __try {
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
            // write_log("ERR", "Unit has no stats.");
            Py_RETURN_NONE;
        }

        struct StatList *statList = unit->pStats; //GetStatList(unit, NULL, 0x40);
        if (!statList) {
            write_log("ERR", "GetStatList returned NULL.");
            Py_RETURN_NONE;
        }

        struct Stat* stats = statList->StatVec.pStats;
        uint32_t statCount = statList->StatVec.wCount;

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
    } __except(EXCEPTION_EXECUTE_HANDLER) {
        write_log("ERR", "crash in py_get_item_stats");
        Py_RETURN_NONE;
    }
}

static PyObject *py_reveal_automap(PyObject *self, PyObject *args) {
    __try {
        struct UnitAny *unit = GetPlayerUnit();
        if (!unit || !unit->pPath || !unit->pPath->pRoom1 || !unit->pPath->pRoom1->pRoom2 || !unit->pPath->pRoom1->pRoom2->pLevel) {
            Py_RETURN_NONE;
        }
        for (int i = 1; i <= 5; i++) {
            reveal_act(i);
        }
        Py_RETURN_NONE;
    } __except(EXCEPTION_EXECUTE_HANDLER) {
        write_log("ERR", "crash in py_reveal_automap");
        Py_RETURN_NONE;
    }
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
    __try {
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
    } __except(EXCEPTION_EXECUTE_HANDLER) {
        write_log("ERR", "crash in py_print_game_string");
        Py_RETURN_NONE;
    }
}

static PyMemberDef PyControl_members[] = {
    {"type", T_UINT, offsetof(PyControl, type), READONLY, ""},
    {"x", T_UINT, offsetof(PyControl, x), READONLY, ""},
    {"y", T_UINT, offsetof(PyControl, y), READONLY, ""},
    {"size_x", T_UINT, offsetof(PyControl, size_x), READONLY, ""},
    {"size_y", T_UINT, offsetof(PyControl, size_y), READONLY, ""},
    {"ptr", T_ULONGLONG, offsetof(PyControl, ptr), READONLY, ""},
    {NULL}
};

static PyObject *py_mouse_click(PyObject *self, PyObject *args) {
    __try {
        int x, y, button, down;
        if (!PyArg_ParseTuple(args, "iiii", &x, &y, &button, &down)) {
            write_log("WRN", "could not parse mouse_click arguments");
            return NULL;
        }

        uint32_t msg;
        if (button == 0) {
            msg = down ? WM_LBUTTONDOWN : WM_LBUTTONUP;
        } else if (button == 1) {
            msg = down ? WM_RBUTTONDOWN : WM_RBUTTONUP;
        } else {
            write_log("WRN", "button must be 0 (left) or 1 (right)");
            PyErr_SetString(PyExc_ValueError, "button must be 0 (left) or 1 (right)");
            return NULL;
        }

        send_mouse_click(x, y, msg);
        Py_RETURN_NONE;
    } __except(EXCEPTION_EXECUTE_HANDLER) {
        write_log("ERR", "crash in py_mouse_click");
        Py_RETURN_NONE;
    }
}

static PyObject *PyControl_get_text(PyControl *self, void *closure) {
    __try {
        struct Control *c = (struct Control *)self->ptr;
        if (!c) Py_RETURN_NONE;

        if (c->dwType == CONTROL_TEXTBOX) {
            if (c->pFirstText && c->pFirstText->pNext && c->pFirstText->pNext->wText[0])
                return PyUnicode_FromWideChar(c->pFirstText->pNext->wText[0], -1);
        } else {
            if (c->wText2)
                return PyUnicode_FromWideChar(c->wText2, -1);
        }

        Py_RETURN_NONE;
    } __except(EXCEPTION_EXECUTE_HANDLER) {
        write_log("ERR", "crash in PyControl_get_text");
        Py_RETURN_NONE;
    }
}

static PyObject *PyControl_get_text_list(PyControl *self, void *closure) {
    __try {
        struct Control *c = (struct Control *)self->ptr;
        if (!c || !c->pFirstText) {
            return PyList_New(0);
        }

        PyObject *list = PyList_New(0);
        struct ControlText *cur = c->pFirstText;
        while (cur) {
            if (cur->wText[0]) {
                PyObject *str = PyUnicode_FromWideChar(cur->wText[0], -1);
                if (str) PyList_Append(list, str);
                Py_XDECREF(str);  // if Append fails, this will avoid leak
            }
            cur = cur->pNext;
        }
        return list;
    } __except(EXCEPTION_EXECUTE_HANDLER) {
        write_log("ERR", "crash in PyControl_get_text_list");
        Py_RETURN_NONE;
    }
}

static PyGetSetDef PyControl_getset[] = {
    {"text", (getter)PyControl_get_text, NULL, "Main control text", NULL},
    {"text_list", (getter)PyControl_get_text_list, NULL, "List of control strings", NULL},
    {NULL}
};

static PyTypeObject PyControlType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "game.Control",
    .tp_basicsize = sizeof(PyControl),
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_members = PyControl_members,
    .tp_getset = PyControl_getset,
};

static PyObject *build_control(struct Control *c) {
    if (!c) {
        write_log("ERR", "build_control called with NULL");
        Py_RETURN_NONE;
    }

    PyControl *obj = PyObject_New(PyControl, &PyControlType);
    if (!obj) {
        write_log("ERR", "Failed to allocate PyControl object");
        return NULL;
    }

    obj->type = c->dwType;
    obj->x = c->dwPosX;
    obj->y = c->dwPosY;
    obj->size_x = c->dwSizeX;
    obj->size_y = c->dwSizeY;
    obj->ptr = c;

    return (PyObject *)obj;
}

static PyObject *py_get_all_controls(PyObject *self, PyObject *args) {
    __try {
        PyObject *list = PyList_New(0);
        struct Control *cur = *first_control;
        int count = 0;
        int max_controls = 500;

        while (cur && count < max_controls) {
            PyObject *py_control = build_control(cur);
            if (!py_control) {
                write_log("ERR", "build_control returned NULL at index %d (control ptr: %p)", count, cur);
                break;
            }

            if (PyList_Append(list, py_control) != 0) {
                write_log("ERR", "PyList_Append failed at index %d", count);
            }

            cur = cur->pNext;
            count++;
        }

        if (count >= max_controls) {
            write_log("WRN", "get_all_controls loop hit max limit (%d)", max_controls);
        }
        return list;
    } __except(EXCEPTION_EXECUTE_HANDLER) {
        write_log("ERR", "crash in py_get_player_level");
        Py_RETURN_NONE;
    }
}

static PyObject *py_set_control_text(PyObject *self, PyObject *args) {
    __try {
        PyObject *py_control;
        const char *text;

        if (!PyArg_ParseTuple(args, "Os", &py_control, &text)) {
            return NULL;
        }

        if (!PyObject_TypeCheck(py_control, &PyControlType)) {
            PyErr_SetString(PyExc_TypeError, "First argument must be a game.Control");
            return NULL;
        }

        PyControl *ctrl = (PyControl *)py_control;
        struct Control *native = (struct Control *)ctrl->ptr;

        // if (ClientState() != ClientStateMenu || !native || !text) {
        if (!native || !text) {
            Py_RETURN_NONE;
        }

        int len = MultiByteToWideChar(CP_UTF8, 0, text, -1, NULL, 0);
        if (len <= 0) {
            PyErr_SetString(PyExc_ValueError, "Failed to convert text to wide string.");
            return NULL;
        }

        wchar_t *wide_text = (wchar_t *)malloc(len * sizeof(wchar_t));
        if (!wide_text) {
            PyErr_NoMemory();
            return NULL;
        }

        MultiByteToWideChar(CP_UTF8, 0, text, -1, wide_text, len);
        SetControlText(native, wide_text);
        free(wide_text);

        Py_RETURN_NONE;
    } __except(EXCEPTION_EXECUTE_HANDLER) {
        write_log("ERR", "crash in py_get_player_level");
        Py_RETURN_NONE;
    }
}

static PyObject *py_get_character_controls(PyObject *self, PyObject *args) {
    __try {
        PyControl *py_start;
        if (!PyArg_ParseTuple(args, "O!", &PyControlType, &py_start)) {
            PyErr_SetString(PyExc_TypeError, "Expected a Control");
            return NULL;
        }

        struct Control *pControl = (struct Control *)py_start->ptr;
        PyObject *list = PyList_New(0);

        while (pControl != NULL) {
            if (pControl->dwType == CONTROL_TEXTBOX &&
                pControl->pFirstText != NULL &&
                pControl->pFirstText->pNext != NULL)
            {
                PyObject *wrapped = build_control(pControl);
                if (wrapped)
                    PyList_Append(list, wrapped);
                Py_XDECREF(wrapped);
            }

            pControl = pControl->pNext;
        }

        return list;
    } __except(EXCEPTION_EXECUTE_HANDLER) {
        write_log("ERR", "crash in py_get_character_controls");
        Py_RETURN_NONE;
    }
}

static PyObject *PyAct_new(PyTypeObject *type, PyObject *args, PyObject *kwds) {
    PyAct *self;
    self = (PyAct *)type->tp_alloc(type, 0);
    return (PyObject *)self;
}

static PyMemberDef PyAct_members[] = {
    {"dwMapSeed", T_UINT, offsetof(PyAct, dwMapSeed), READONLY, ""},
    {NULL}
};

static PyTypeObject PyActType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "game.Act",
    .tp_basicsize = sizeof(PyAct),
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = PyAct_new,
    .tp_members = PyAct_members,
};

static PyObject *build_act(struct Act *act) {
    if (!act) Py_RETURN_NONE;

    PyAct *py_act = PyObject_New(PyAct, &PyActType);
    if (!py_act) return NULL;

    py_act->act = act;
    py_act->dwMapSeed = act->dwMapSeed;
    py_act->pRoom1 = act->pRoom1;
    py_act->pMisc = act->pMisc;

    return (PyObject *)py_act;
}

static PyObject *PyActMisc_new(PyTypeObject *type, PyObject *args, PyObject *kwds) {
    PyActMisc *self;
    self = (PyActMisc *)type->tp_alloc(type, 0);
    return (PyObject *)self;
}

static PyMemberDef PyActMisc_members[] = {
    {"dwStaffTombLevel", T_UINT, offsetof(PyActMisc, dwStaffTombLevel), READONLY, ""},
    {NULL}
};

static PyObject *py_get_player_act(PyObject *self, PyObject *args) {
    __try {
        PyObject *py_unit;
        if (!PyArg_ParseTuple(args, "O!", &PyUnitType, &py_unit)) {
            PyErr_SetString(PyExc_TypeError, "Expected a Unit");
            return NULL;
        }

        PyUnit *unit = (PyUnit *)py_unit;
        if (!unit->pAct) {
            Py_RETURN_NONE;
        }

        return build_act(unit->pAct);
    } __except(EXCEPTION_EXECUTE_HANDLER) {
        write_log("ERR", "crash in py_get_player_act");
        Py_RETURN_NONE;
    }
}

static PyTypeObject PyActMiscType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "game.ActMisc",
    .tp_basicsize = sizeof(PyActMisc),
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = PyActMisc_new,
    .tp_members = PyActMisc_members,
};

static PyObject *build_act_misc(struct ActMisc *misc) {
    if (!misc) Py_RETURN_NONE;

    PyActMisc *py_misc = PyObject_New(PyActMisc, &PyActMiscType);
    if (!py_misc) return NULL;

    py_misc->misc = misc;
    py_misc->dwStaffTombLevel = misc->dwStaffTombLevel;
    py_misc->pLevelFirst = misc->pLevelFirst;

    return (PyObject *)py_misc;
}

static PyObject *PyLevel_new(PyTypeObject *type, PyObject *args, PyObject *kwds) {
    PyLevel *self;
    self = (PyLevel *)type->tp_alloc(type, 0);
    return (PyObject *)self;
}

static PyMemberDef PyLevel_members[] = {
    {"level_no", T_UINT, offsetof(PyLevel, level_no), READONLY, ""},
    {"pos_x", T_UINT, offsetof(PyLevel, pos_x), READONLY, ""},
    {"pos_y", T_UINT, offsetof(PyLevel, pos_y), READONLY, ""},
    {"size_x", T_UINT, offsetof(PyLevel, size_x), READONLY, ""},
    {"size_y", T_UINT, offsetof(PyLevel, size_y), READONLY, ""},
    {NULL}
};

static PyTypeObject PyLevelType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "game.Level",
    .tp_basicsize = sizeof(PyLevel),
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = PyLevel_new,
    .tp_members = PyLevel_members,
};

static PyObject *build_level_object(struct Level *level) {
    if (!level) Py_RETURN_NONE;

    PyLevel *obj = PyObject_New(PyLevel, &PyLevelType);
    if (!obj) return NULL;

    obj->level = level;
    obj->level_no = level->dwLevelNo;
    obj->pos_x = level->dwPosX;
    obj->pos_y = level->dwPosY;
    obj->size_x = level->dwSizeX;
    obj->size_y = level->dwSizeY;

    return (PyObject *)obj;
}

static PyObject *py_get_player_level(PyObject *self, PyObject *args) {
    __try {
        PyUnit *py_unit;

        if (!PyArg_ParseTuple(args, "O!", &PyUnitType, &py_unit)) {
            PyErr_SetString(PyExc_TypeError, "Expected a Unit");
            return NULL;
        }

        if (!py_unit->unit || !py_unit->unit->pPath ||
            !py_unit->unit->pPath->pRoom1 ||
            !py_unit->unit->pPath->pRoom1->pRoom2 ||
            !py_unit->unit->pPath->pRoom1->pRoom2->pLevel) {
            Py_RETURN_NONE;
            }

        return build_level_object(py_unit->unit->pPath->pRoom1->pRoom2->pLevel);
    } __except(EXCEPTION_EXECUTE_HANDLER) {
        write_log("ERR", "crash in py_get_player_level");
        Py_RETURN_NONE;
    }
}

static PyObject *py_get_act_levels(PyObject *self, PyObject *args) {
    __try {
        PyAct *py_act;

        if (!PyArg_ParseTuple(args, "O!", &PyActType, &py_act)) {
            PyErr_SetString(PyExc_TypeError, "Expected an Act");
            return NULL;
        }

        if (!py_act->act || !py_act->pMisc || !py_act->pMisc->pLevelFirst) {
            Py_RETURN_NONE;
        }

        PyObject *list = PyList_New(0);
        struct Level *level = py_act->pMisc->pLevelFirst;

        while (level) {
            PyObject *py_level = build_level_object(level);
            if (py_level)
                PyList_Append(list, py_level);
            Py_XDECREF(py_level);
            level = level->pNextLevel;
        }

        return list;
    } __except(EXCEPTION_EXECUTE_HANDLER) {
        write_log("ERR", "crash in py_get_act_levels");
        Py_RETURN_NONE;
    }
}

static PyObject *PyMapRoom_new(PyTypeObject *type, PyObject *args, PyObject *kwds) {
    PyMapRoom *self;
    self = (PyMapRoom *)type->tp_alloc(type, 0);
    return (PyObject *)self;
}

static PyMemberDef PyMapRoom_members[] = {
    {"pos_x", T_UINT, offsetof(PyMapRoom, pos_x), READONLY, ""},
    {"pos_y", T_UINT, offsetof(PyMapRoom, pos_y), READONLY, ""},
    {"size_x", T_UINT, offsetof(PyMapRoom, size_x), READONLY, ""},
    {"size_y", T_UINT, offsetof(PyMapRoom, size_y), READONLY, ""},
    {NULL}
};

static PyTypeObject PyMapRoomType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "game.MapRoom",
    .tp_basicsize = sizeof(PyMapRoom),
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = PyMapRoom_new,
    .tp_members = PyMapRoom_members,
};

static PyObject *build_map_room_from_room2(struct Room2 *room2) {
    if (!room2) Py_RETURN_NONE;

    PyMapRoom *obj = PyObject_New(PyMapRoom, &PyMapRoomType);
    if (!obj) return NULL;

    obj->room_data = room2;
    obj->pos_x = room2->dwPosX;
    obj->pos_y = room2->dwPosY;
    obj->size_x = room2->dwSizeX;
    obj->size_y = room2->dwSizeY;

    return (PyObject *)obj;
}

static PyObject *py_get_player_map_room(PyObject *self, PyObject *args) {
    __try {
        PyUnit *py_unit;
        if (!PyArg_ParseTuple(args, "O!", &PyUnitType, &py_unit)) {
            PyErr_SetString(PyExc_TypeError, "Expected a Unit");
            return NULL;
        }

        if (!py_unit->unit || !py_unit->unit->pPath || !py_unit->unit->pPath->pRoom1 || !py_unit->unit->pPath->pRoom1->pRoom2) {
            Py_RETURN_NONE;
        }

        return build_map_room_from_room2(py_unit->unit->pPath->pRoom1->pRoom2);
    } __except(EXCEPTION_EXECUTE_HANDLER) {
        write_log("ERR", "crash in py_get_player_map_room");
        Py_RETURN_NONE;
    }
}

static PyObject *py_get_level_map_rooms(PyObject *self, PyObject *args) {
    __try {
        PyLevel *py_level;

        if (!PyArg_ParseTuple(args, "O!", &PyLevelType, &py_level)) {
            PyErr_SetString(PyExc_TypeError, "Expected a game.Level");
            return NULL;
        }

        struct Level *level = py_level->level;
        if (!level || !level->pRoom2First) {
            Py_RETURN_NONE;
        }

        // if (level->pMisc && level->pRoom2First && !level->pRoom2First->pRoom1) {
        //     write_log("INF", "InitLevel");
        //     InitLevel(level);
        // }

        PyObject *list = PyList_New(0);
        if (!list) return NULL;

        for (struct Room2 *room2 = level->pRoom2First; room2; room2 = room2->pRoom2Next) {
            bool added = false;

            if (!room2->pRoom1 && (room2->dwRoomFlags & 1)) {
                AddRoomData(level->pMisc->pAct, level->dwLevelNo, room2->dwPosX, room2->dwPosY, room2);
                added = true;
            }

            if (room2->pRoom1) {
                PyObject *room = build_map_room_from_room2(room2);
                if (room) {
                    PyList_Append(list, room);
                    Py_DECREF(room);
                }
            }

            if (added) {
                // RemoveRoomData(level->pMisc->pAct, level->dwLevelNo, room2->dwPosX, room2->dwPosY, room2);
            }
        }

        return list;
    } __except(EXCEPTION_EXECUTE_HANDLER) {
        write_log("ERR", "crash in py_get_level_map_rooms");
        Py_RETURN_NONE;
    }
}

static PyObject *py_get_level_exits(PyObject *self, PyObject *args) {
    __try {
        PyLevel *py_level;

        if (!PyArg_ParseTuple(args, "O!", &PyLevelType, &py_level)) {
            PyErr_SetString(PyExc_TypeError, "Expected a game.Level");
            return NULL;
        }

        struct Level *level = py_level->level;
        if (!level || !level->pRoom2First) {
            Py_RETURN_NONE;
        }

        PyObject *result_list = PyList_New(0);
        if (!result_list) return NULL;

        for (struct Room2 *room = level->pRoom2First; room; room = room->pRoom2Next) {
            bool addedRoomData = false;

            if (!room->pRoom1) {
                AddRoomData(level->pMisc->pAct, level->dwLevelNo, room->dwPosX, room->dwPosY, room);
                addedRoomData = true;
            }

            if (!room->pRoom2Near || room->dwRoomsNear > 64) continue;

            for (int i = 0; i < room->dwRoomsNear; i++) {
                struct Room2 *neighbor = room->pRoom2Near[i];

                if (!neighbor || !neighbor->pLevel) continue;
                if (neighbor->pLevel->dwLevelNo == room->pLevel->dwLevelNo) continue;

                // De-duplication: skip if already added
                bool already_exists = false;
                Py_ssize_t len = PyList_Size(result_list);
                for (Py_ssize_t j = 0; j < len; j++) {
                    PyObject *entry = PyList_GetItem(result_list, j);
                    if (!entry) continue;

                    PyObject *from_val = PyDict_GetItemString(entry, "from");
                    PyObject *to_val = PyDict_GetItemString(entry, "to");

                    if (from_val && to_val &&
                        PyLong_AsUnsignedLong(from_val) == room->pLevel->dwLevelNo &&
                        PyLong_AsUnsignedLong(to_val) == neighbor->pLevel->dwLevelNo) {
                        already_exists = true;
                        break;
                    }
                }

                if (already_exists) continue;

                PyObject *exit_dict = PyDict_New();
                if (!exit_dict) continue;

                PyDict_SetItemString(exit_dict, "from", PyLong_FromUnsignedLong(room->pLevel->dwLevelNo));
                PyDict_SetItemString(exit_dict, "to", PyLong_FromUnsignedLong(neighbor->pLevel->dwLevelNo));
                PyDict_SetItemString(exit_dict, "x", PyLong_FromUnsignedLong(room->dwPosX * 5 + room->dwSizeX * 5 / 2));
                PyDict_SetItemString(exit_dict, "y", PyLong_FromUnsignedLong(room->dwPosY * 5 + room->dwSizeY * 5 / 2));

                PyList_Append(result_list, exit_dict);
                Py_DECREF(exit_dict);
            }

            if (addedRoomData) {
                // RemoveRoomData(level->pMisc->pAct, level->dwLevelNo, room->dwPosX, room->dwPosY, room);
            }
        }

        return result_list;

    } __except(EXCEPTION_EXECUTE_HANDLER) {
        write_log("ERR", "crash in py_get_level_exits");
        Py_RETURN_NONE;
    }
}

static PyObject *build_object_unit(struct UnitAny *unit) {
    if (!unit) Py_RETURN_NONE;

    PyUnit *py_unit = PyObject_New(PyUnit, &PyUnitType);
    py_unit->unit = unit;
    py_unit->id = unit->dwUnitId;
    py_unit->type = unit->dwType;
    py_unit->dwTxtFileNo = unit->dwTxtFileNo;
    py_unit->dwMode = unit->dwMode;
    py_unit->pAct = unit->pAct;

    if (unit->pObjectPath) {
        py_unit->pItemPathdwPosX = unit->pObjectPath->dwPosX;
        py_unit->pItemPathdwPosY = unit->pObjectPath->dwPosY;
    } else {
        py_unit->pItemPathdwPosX = 0;
        py_unit->pItemPathdwPosY = 0;
    }

    return (PyObject *)py_unit;
}

static PyObject *py_get_nearby_units(PyObject *self, PyObject *args) {
    __try {
        PyObject *list = PyList_New(0);
        if (!list) {
            write_log("ERR", "level_units: PyList_New failed");
            return NULL;
        }

        for (int type = 0; type <= 5; ++type) {
            struct UnitHashTable *table = (type == UNIT_MISSILE) ? client_side_units : server_side_units;
            if (!table) continue;

            for (int i = 0; i < 128; ++i) {
                struct UnitAny *unit = table[type].table[i];
                while (unit) {
                    PyObject *obj = NULL;

                    switch (unit->dwType) {
                        case UNIT_OBJECT:
                            obj = build_object_unit(unit);
                            break;
                        case UNIT_MONSTER:
                            obj = build_monster_unit(unit);
                            break;
                        case UNIT_PLAYER:
                            obj = build_player_unit(unit);
                            break;
                        case UNIT_ITEM:
                            obj = build_item_unit(unit);
                            break;
                        default:
                            break;
                    }

                    if (obj) {
                        if (PyList_Append(list, obj) != 0) {
                            write_log("ERR", "level_units: PyList_Append failed");
                            Py_DECREF(obj);
                            Py_DECREF(list);
                            return NULL;
                        }
                        Py_DECREF(obj);
                    }

                    unit = unit->pListNext;
                }
            }
        }

        if (PyErr_Occurred()) {
            write_log("ERR", "level_units: exception set");
            Py_DECREF(list);
            return NULL;
        }

        return list;
    } __except(EXCEPTION_EXECUTE_HANDLER) {
        write_log("ERR", "crash in py_get_nearby_units");
        Py_RETURN_NONE;
    }
}

PyObject *py_get_unit_name(PyObject *self, PyObject *args) {
    __try {
        PyObject *py_unit;
        if (!PyArg_ParseTuple(args, "O", &py_unit)) {
            Py_RETURN_NONE;
        }

        if (!PyObject_TypeCheck(py_unit, &PyUnitType)) {
            Py_RETURN_NONE;
        }

        PyUnit *unit = (PyUnit *)py_unit;
        if (!unit->unit) {
            Py_RETURN_NONE;
        }

        char szTmp[256] = {0};

        switch (unit->unit->dwType) {
            case UNIT_MONSTER: {
                wchar_t *wName = get_unit_name((uintptr_t)unit->unit);
                if (wName) {
                    WideCharToMultiByte(CP_ACP, 0, wName, -1, szTmp, sizeof(szTmp), 0, 0);
                    return PyUnicode_FromString(szTmp);
                }
                break;
            }
            case UNIT_PLAYER: {
                if (unit->unit->pPlayerData) {
                    strncpy(szTmp, unit->unit->pPlayerData->szName, sizeof(szTmp) - 1);
                    return PyUnicode_FromString(szTmp);
                }
                break;
            }
            case UNIT_ITEM: {
                wchar_t wBuffer[256] = {0};
                GetItemName(unit->unit, wBuffer, sizeof(wBuffer));
                char *szBuffer = UnicodeToAnsi(wBuffer);
                if (!szBuffer) break;
                char *newline = strchr(szBuffer, '\n');
                if (newline) *newline = 0x00;
                strncpy(szTmp, szBuffer, sizeof(szTmp) - 1);
                free(szBuffer);
                return PyUnicode_FromString(szTmp);
            }
            case UNIT_OBJECT:
            case UNIT_TILE: {
                if (unit->unit->pObjectData && unit->unit->pObjectData->pTxt) {
                    strncpy(szTmp, unit->unit->pObjectData->pTxt->szName, sizeof(szTmp) - 1);
                    return PyUnicode_FromString(szTmp);
                }
                break;
            }
            default:
                break;
        }

        return PyUnicode_FromString("Unknown");
    } __except(EXCEPTION_EXECUTE_HANDLER) {
        write_log("ERR", "crash in py_get_unit_name");
        Py_RETURN_NONE;
    }
}

static PyMemberDef PyPreset_members[] = {
    {"type", T_UINT, offsetof(PyPreset, type), READONLY, ""},
    {"id", T_UINT, offsetof(PyPreset, id), READONLY, ""},
    {"x", T_UINT, offsetof(PyPreset, x), READONLY, ""},
    {"y", T_UINT, offsetof(PyPreset, y), READONLY, ""},
    {NULL}
};

PyTypeObject PyPresetType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "game.Preset",
    .tp_basicsize = sizeof(PyPreset),
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_doc = "Preset unit",
    .tp_members = PyPreset_members,
};

static PyObject *build_preset(struct PresetUnit *preset, uint32_t roomx, uint32_t roomy) {
    if (!preset) Py_RETURN_NONE;

    PyPreset *obj = PyObject_New(PyPreset, &PyPresetType);
    if (!obj) return NULL;

    obj->preset = preset;
    obj->type = preset->dwType;
    obj->id = preset->dwTxtFileNo;
    obj->x = roomx * 5 + preset->dwPosX;
    obj->y = roomy * 5 + preset->dwPosY;

    return (PyObject *)obj;
}

static PyObject *py_get_presets_for_room(PyObject *self, PyObject *args) {
    __try {
        PyMapRoom *py_room;
        if (!PyArg_ParseTuple(args, "O!", &PyMapRoomType, &py_room))
            return NULL;

        struct Room2 *room = py_room->room_data;
        if (!room || !room->pPreset)
            Py_RETURN_NONE;

        PyObject *list = PyList_New(0);
        if (!list) return NULL;

        for (struct PresetUnit *preset = room->pPreset; preset; preset = preset->pPresetNext) {
            PyObject *obj = build_preset(preset, room->dwPosX, room->dwPosY);
            if (!obj) continue;
            PyList_Append(list, obj);
            Py_DECREF(obj);
        }

        return list;
    } __except(EXCEPTION_EXECUTE_HANDLER) {
        write_log("ERR", "crash in py_get_nearby_units");
        Py_RETURN_NONE;
    }
}

static PyMemberDef PyTile_members[] = {
    {"level_x", T_UINT, offsetof(PyTile, level_x), READONLY, ""},
    {"level_y", T_UINT, offsetof(PyTile, level_y), READONLY, ""},
    {"flags", T_USHORT, offsetof(PyTile, flags), READONLY, ""},
    {NULL}
};

static PyTypeObject PyTileType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "game.Tile",
    .tp_basicsize = sizeof(PyTile),
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_members = PyTile_members,
};

static PyObject *build_tile(uint32_t level_x, uint32_t level_y, uint16_t flags) {
    PyTile *tile = PyObject_New(PyTile, &PyTileType);
    if (!tile) return NULL;

    tile->level_x = level_x;
    tile->level_y = level_y;
    tile->flags = flags;

    return (PyObject *)tile;
}

static PyObject *py_get_room_tiles(PyObject *self, PyObject *args) {
    __try {
        PyMapRoom *py_room;
        if (!PyArg_ParseTuple(args, "O!", &PyMapRoomType, &py_room))
            return NULL;

        struct Room2 *room2 = py_room->room_data;
        if (!room2 || !room2->pLevel || !room2->pLevel->pMisc)
            Py_RETURN_NONE;

        bool addedRoomData = false;
        if (!room2->pRoom1) {
            AddRoomData(room2->pLevel->pMisc->pAct, room2->pLevel->dwLevelNo,
                        room2->dwPosX, room2->dwPosY, room2);
            addedRoomData = true;
        }

        if (!room2->pRoom1 || !room2->pRoom1->Coll || !room2->pRoom1->Coll->pMapStart)
            goto fail;

        struct CollMap *coll = room2->pRoom1->Coll;
        int size_x = coll->dwSizeRoomX;
        int size_y = coll->dwSizeRoomY;
        uint16_t *flags = coll->pMapStart;

        PyObject *list = PyList_New(0);
        if (!list)
            goto fail;

        for (int y = 0; y < size_y * 5; y++) {
            for (int x = 0; x < size_x * 5; x++) {
                int index = y * size_x + x;
                uint16_t flag = flags[index];
                uint32_t level_x = coll->dwPosGameX + x;
                uint32_t level_y = coll->dwPosGameY + y;

                struct UnitAny *player = GetPlayerUnit();
                if (!(abs((int)level_x - player->pPath->xPos) > 5 || abs((int)level_y - player->pPath->yPos) > 5)) {
                    write_log("DBG", "tile (%u,%u) flag=0x%04x", level_x, level_y, flag);
                }

                PyObject *tile = build_tile(level_x, level_y, flag);
                if (!tile || PyList_Append(list, tile) != 0) {
                    Py_XDECREF(tile);
                    Py_DECREF(list);
                    goto fail;
                }

                Py_DECREF(tile);
            }
        }

        if (addedRoomData) {
            // RemoveRoomData(room2->pLevel->pMisc->pAct, room2->pLevel->dwLevelNo,
                           // room2->dwPosX, room2->dwPosY, room2);
        }

        return list;

        fail:
            if (addedRoomData) {
                // RemoveRoomData(room2->pLevel->pMisc->pAct, room2->pLevel->dwLevelNo,
                               // room2->dwPosX, room2->dwPosY, room2);
            }
        Py_RETURN_NONE;
    } __except(EXCEPTION_EXECUTE_HANDLER) {
        write_log("ERR", "crash in py_get_nearby_units");
        Py_RETURN_NONE;
    }
}

static PyObject *py_get_map_room_neighbors(PyObject *self, PyObject *args) {
    __try {
        PyMapRoom *py_room;
        if (!PyArg_ParseTuple(args, "O!", &PyMapRoomType, &py_room))
            return NULL;

        struct Room2 *room = py_room->room_data;
        if (!room || !room->pRoom2Near || room->dwRoomsNear == 0)
            Py_RETURN_NONE;

        PyObject *list = PyList_New(0);
        if (!list) return NULL;

        for (uint32_t i = 0; i < room->dwRoomsNear; i++) {
            struct Room2 *neighbor = room->pRoom2Near[i];
            if (!neighbor) continue;

            PyObject *map_room = build_map_room_from_room2(neighbor);
            if (map_room) {
                PyList_Append(list, map_room);
                Py_DECREF(map_room);
            }
        }

        return list;
    } __except(EXCEPTION_EXECUTE_HANDLER) {
        write_log("ERR", "crash in py_get_map_room_neighbors");
        Py_RETURN_NONE;
    }
}

static PyObject *py_world_to_automap(PyObject *self, PyObject *args) {
    uint32_t x, y;
    if (!PyArg_ParseTuple(args, "II", &x, &y)) {
        return NULL;
    }

    POINT pt = {0};
    world_to_automap(&pt, x, y);

    return Py_BuildValue("(ii)", pt.x, pt.y);
}

void __stdcall map_to_abs_screen(POINT *pos) {
    int x = pos->x;
    int y = pos->y;

    int screenX = 16 * (x - y);
    int screenY = 8 * (x + y);

    pos->x = screenX;
    pos->y = screenY;
}

static PyObject *py_click_map(PyObject *self, PyObject *args) {
    __try {
        int click_type;
        int x, y;
        int shift = 0;
        PyObject *py_unit = NULL;

        if (!PyArg_ParseTuple(args, "iii|O", &click_type, &x, &y, &py_unit)) {
            return NULL;
        }

        struct UnitAny *unit = NULL;
        if (py_unit && PyObject_TypeCheck(py_unit, &PyUnitType)) {
            unit = ((PyUnit *)py_unit)->unit;
        }

        POINT Click = { .x = x , .y = y };

        if (unit) {
            write_log("DBG", "GetUnitX %i", x);
            Click.x = (long)GetUnitX(unit);
            write_log("DBG", "GetUnitY %i", y);
            Click.y = (long)GetUnitY(unit);
        }

        write_log("DBG", "MapToAbsScreen %i %i", x, y);
        map_to_abs_screen(&Click);
        // world_to_automap(&Click, x, y);
        write_log("DBG", "viewport_x %i", (long)*viewport_x);
        Click.x -= (long)*viewport_x;
        write_log("DBG", "viewport_y %i", (long)*viewport_y);
        Click.y -= (long)*viewport_y;

        write_log("DBG", "click_x %i", Click.x);
        write_log("DBG", "click_y %i", Click.y);

        write_log("DBG", "mouse_x %i", (long)*mouse_x);
        write_log("DBG", "mouse_y %i", (long)*mouse_y);
        POINT OldMouse = {
            .x = (long)*mouse_x,
            .y = (long)*mouse_y
        };

        *mouse_x = 0;
        *mouse_y = 0;

        int flags = shift ? 0x0C : (*always_run ? 0x08 : 0);

        if (unit && unit != GetPlayerUnit()) {
            write_log("DBG", "ClickMap1");
            ClickMap(click_type, Click.x, Click.y, flags);
            write_log("DBG", "set_selected_unit");
            set_selected_unit(NULL);
        } else {
            write_log("DBG", "ClickMap2");
            ClickMap(click_type, Click.x, Click.y, flags);
        }

        write_log("DBG", "mouse_x");
        *mouse_x = OldMouse.x;
        write_log("DBG", "mouse_y");
        *mouse_y = OldMouse.y;
        write_log("DBG", "done");

        Py_RETURN_TRUE;
    } __except(EXCEPTION_EXECUTE_HANDLER) {
        write_log("ERR", "crash in py_click_map");
        Py_RETURN_NONE;
    }
}

static PyObject *py_get_blocked_automap_tiles(PyObject *self, PyObject *args) {
    __try {
        PyObject *list = PyList_New(0);
        if (!list)
            return NULL;

        struct AutomapLayer *layer = *automap_layer;
        if (!layer)
            Py_RETURN_NONE;

        struct UnitAny *player = GetPlayerUnit();

        while (layer) {
            struct AutomapCell *cells[] = {
                layer->pWalls,
                layer->pObjects,
                layer->pExtras,
                layer->pFloors
            };

            for (int i = 0; i < 4; i++) {
                struct AutomapCell *cell = cells[i];
                while (cell) {
                    int sx = cell->xPixel / 32;
                    int sy = cell->yPixel / 16;
                    int tile_x = (sx + sy) / 2;
                    int tile_y = (sy - sx) / 2;

                    PyObject *tuple = Py_BuildValue("(ii)", tile_x, tile_y);
                    PyList_Append(list, tuple);
                    Py_DECREF(tuple);
                    cell = cell->pMore;
                }
            }

            layer = layer->pNextLayer;
        }

        return list;
    } __except(EXCEPTION_EXECUTE_HANDLER) {
        write_log("ERR", "crash in py_get_blocked_automap_tiles");
        Py_RETURN_NONE;
    }
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
    {"get_all_controls", py_get_all_controls, METH_NOARGS, NULL},
    {"mouse_click", py_mouse_click, METH_VARARGS, NULL},
    {"set_control_text", py_set_control_text, METH_VARARGS, NULL},
    {"get_character_controls", py_get_character_controls, METH_VARARGS, NULL},
    {"get_player_act", py_get_player_act, METH_VARARGS, NULL},
    {"get_player_level", py_get_player_level, METH_VARARGS, NULL},
    {"get_act_levels", py_get_act_levels, METH_VARARGS, NULL},
    {"get_player_map_room", py_get_player_map_room, METH_VARARGS, NULL},
    {"get_level_map_rooms", py_get_level_map_rooms, METH_VARARGS, NULL},
    {"get_level_exits", py_get_level_exits, METH_VARARGS, NULL},
    {"get_nearby_units", py_get_nearby_units, METH_NOARGS, NULL},
    {"get_unit_name", py_get_unit_name, METH_VARARGS, NULL},
    {"get_presets_for_room", py_get_presets_for_room, METH_VARARGS, NULL},
    {"get_room_tiles", py_get_room_tiles, METH_VARARGS, NULL},
    {"get_map_room_neighbors", py_get_map_room_neighbors, METH_VARARGS, NULL},
    {"world_to_automap", py_world_to_automap, METH_VARARGS, NULL},
    {"click_map", py_click_map, METH_VARARGS, NULL},
    { "get_blocked_automap_tiles", py_get_blocked_automap_tiles, METH_NOARGS, NULL},
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

    if (PyType_Ready(&PyControlType) < 0) {
        write_log("ERR", "PyControlType not ready");
        return NULL;
    }
    Py_INCREF(&PyControlType);
    PyModule_AddObject(module, "Control", (PyObject *)&PyControlType);

    if (PyType_Ready(&PyActType) < 0) {
        write_log("ERR", "PyActType not ready");
        return NULL;
    }
    Py_INCREF(&PyActType);
    PyModule_AddObject(module, "Act", (PyObject *)&PyActType);

    if (PyType_Ready(&PyActMiscType) < 0) {
        write_log("ERR", "PyActMiscType not ready");
        return NULL;
    }
    Py_INCREF(&PyActMiscType);
    PyModule_AddObject(module, "ActMisc", (PyObject *)&PyActMiscType);

    if (PyType_Ready(&PyLevelType) < 0) {
        write_log("ERR", "PyLevelType not ready");
        return NULL;
    }
    Py_INCREF(&PyLevelType);
    PyModule_AddObject(module, "Level", (PyObject *)&PyLevelType);

    if (PyType_Ready(&PyMapRoomType) < 0) {
        write_log("ERR", "PyMapRoomType not ready");
        return NULL;
    }
    Py_INCREF(&PyMapRoomType);
    PyModule_AddObject(module, "MapRoom", (PyObject *)&PyMapRoomType);

    if (PyType_Ready(&PyPresetType) < 0) {
        write_log("ERR", "PyPresetType not ready");
        return NULL;
    }
    Py_INCREF(&PyPresetType);
    PyModule_AddObject(module, "Preset", (PyObject *)&PyPresetType);

    if (PyType_Ready(&PyTileType) < 0) {
        write_log("ERR", "PyTileType not ready");
        return NULL;
    }
    Py_INCREF(&PyTileType);
    PyModule_AddObject(module, "Tile", (PyObject *)&PyTileType);

    return module;
}
