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

static PyObject *PyUnit_new(PyTypeObject *type, PyObject *args, PyObject *kwds);
static PyObject *py_get_player_unit(PyObject *self, PyObject *args);
static PyObject *py_get_item_table(PyObject *self, PyObject *args);
static PyObject *py_interact(PyObject *self, PyObject *args);
static PyObject *py_write_log(PyObject *self, PyObject *args);

void flex_loop(void);
void automap_loop(void);
PyMODINIT_FUNC PyInit_game(void);

#endif
