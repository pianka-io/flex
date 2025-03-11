#ifndef FLEXLIB_API_H
#define FLEXLIB_API_H

typedef struct {
    PyObject_HEAD
    uint32_t id;
    uint32_t type;
    uint16_t x;
    uint16_t y;
} PyUnit;

static PyObject *PyUnit_new(PyTypeObject *type, PyObject *args, PyObject *kwds);
static int PyUnit_init(PyUnit *self, PyObject *args, PyObject *kwds);
static PyObject *PyUnit_repr(PyUnit *self);
static PyObject *py_get_player_unit(PyObject *self, PyObject *args);
static PyObject *py_get_item_table(PyObject *self, PyObject *args);
static PyObject *py_interact(PyObject *self, PyObject *args);
static PyObject *py_write_log(PyObject *self, PyObject *args);
static PyObject *py_register_tick(PyObject *self, PyObject *args);

void python_tick(void);
PyMODINIT_FUNC PyInit_game(void);
void init_python(void);

#endif
