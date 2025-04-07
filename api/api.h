#ifndef FLEXLIB_API_H
#define FLEXLIB_API_H

typedef struct {
    PyObject_HEAD
    struct UnitAny *unit;
    uint32_t id;
    uint32_t type;
    uint32_t dwTxtFileNo;
    uint32_t dwMode;
    /* item */
    uint32_t pItemDatadwFlags;
    uint32_t pItemDatadwItemLevel;
    struct UnitAny *pItemDatadpOwner;
    uint16_t pItemPathdwPosX;
    uint16_t pItemPathdwPosY;
    uint16_t pItemDatadwQuality;
    /* character */
    uint16_t pPathxPos;
    uint16_t pPathyPos;
    uint32_t dwAct;
    /* monster */
    wchar_t *pMonsterDatawName;
    uint16_t pMonsterDatawUniqueNo;
    uint8_t pMonsterDatafNormal;
    uint8_t pMonsterDatafChamp;
    uint8_t pMonsterDatafBoss;
    uint8_t pMonsterDatafMinion;
    struct Act *pAct;
} PyUnit;

typedef struct {
    PyObject_HEAD
    char *name;
    char *password;
    char *server_ip;
    char *account_name;
    char *character_name;
    char *realm_name;
} PyGameInfo;

typedef struct {
    PyObject_HEAD
    uint32_t type;
    uint32_t x;
    uint32_t y;
    uint32_t size_x;
    uint32_t size_y;
    struct Control *ptr;
} PyControl;

typedef struct {
    PyObject_HEAD
    struct Act *act;
    uint32_t dwMapSeed;
    struct Room1 *pRoom1;
    struct ActMisc *pMisc;
} PyAct;

typedef struct {
    PyObject_HEAD
    struct ActMisc *misc;
    uint32_t dwStaffTombLevel;
    struct Level *pLevelFirst;
} PyActMisc;

typedef struct {
    PyObject_HEAD
    struct Level *level;
    uint32_t level_no;
    uint32_t pos_x;
    uint32_t pos_y;
    uint32_t size_x;
    uint32_t size_y;
    struct Room2 *pRoom2First;
} PyLevel;

typedef struct {
    PyObject_HEAD
    struct Room1 *room;
    struct Room2 *room_data;
    uint32_t pos_x;
    uint32_t pos_y;
    uint32_t size_x;
    uint32_t size_y;
} PyMapRoom;

typedef struct {
    PyObject_HEAD
    struct PresetUnit *preset;

    uint32_t type;
    uint32_t id;
    uint32_t x;
    uint32_t y;
} PyPreset;

static PyObject *PyUnit_new(PyTypeObject *type, PyObject *args, PyObject *kwds);
static PyObject *py_get_player_unit(PyObject *self, PyObject *args);
static PyObject *py_get_item_table(PyObject *self, PyObject *args);
static PyObject *py_interact(PyObject *self, PyObject *args);
static PyObject *py_write_log(PyObject *self, PyObject *args);

void flex_loop(void);
void automap_loop(void);
PyMODINIT_FUNC PyInit_game(void);

#endif
