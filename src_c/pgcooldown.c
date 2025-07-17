#include <math.h>
#include <time.h>
#include <Python.h>


/*----------------------------------------------------------------------
     ____                 _        _                 
    |  _ \  ___   ___ ___| |_ _ __(_)_ __   __ _ ___ 
    | | | |/ _ \ / __/ __| __| '__| | '_ \ / _` / __|
    | |_| | (_) | (__\__ \ |_| |  | | | | | (_| \__ \
    |____/ \___/ \___|___/\__|_|  |_|_| |_|\__, |___/
					   |___/     
----------------------------------------------------------------------*/

#include <docstrings.h>

/*----------------------------------------------------------------------
     ____        __ _       _ _   _                 
    |  _ \  ___ / _(_)_ __ (_) |_(_) ___  _ __  ___ 
    | | | |/ _ \ |_| | '_ \| | __| |/ _ \| '_ \/ __|
    | |_| |  __/  _| | | | | | |_| | (_) | | | \__ \
    |____/ \___|_| |_|_| |_|_|\__|_|\___/|_| |_|___/
                                                
----------------------------------------------------------------------*/

#define MAX(a, b) (((a) > (b)) ? (a) : (b))
#define T_FRACTION_SCALE 1000000000.0

typedef struct Cooldown {
    PyObject_HEAD
    struct timespec t0;
    double duration;
    int wrap;
    int paused;
    double remaining_; /* Save remaining duration when paused */
} Cooldown;

/* Utilities */
static void dump(char *msg, Cooldown *self);

static double lerp(double a, double b, double t);
static double invlerp(double a, double b, double v);
static double remap(double a0, double a1, double b0, double b1, double v);

static double timespec_to_double(struct timespec *t);
static void double_to_timespec(struct timespec *t, double val);
static double diff_timespec(struct timespec *t0, struct timespec *t1);
static void substract_timespec(struct timespec *t0, struct timespec *t1);
static double current_delta(struct timespec *t0);

static double get_temperature(Cooldown *self);
static void set_temperature(Cooldown *self, double val);
static double get_remaining(Cooldown *self);
static void set_remaining(Cooldown *self, double val);
static int is_cold(Cooldown *self);
static void set_cold(Cooldown *self, int val);
static void set_paused(Cooldown *self, int val);

/* Module level functions */
static PyObject * pgcooldown_lerp(PyObject *self, PyObject *const *args, Py_ssize_t nargs);
static PyObject * pgcooldown_invlerp(PyObject *self, PyObject *const *args, Py_ssize_t nargs);
static PyObject * pgcooldown_remap(PyObject *self, PyObject *const *args, Py_ssize_t nargs);
static PyObject * cooldown_new(PyTypeObject *type, PyObject *args, PyObject *kwargs);

/* Class definition */
static PyTypeObject cooldown_type;
static int cooldown___init__(Cooldown *self, PyObject *args, PyObject *kwargs);
static void cooldown_dealloc(Cooldown *self);

/* Class methods */
static PyObject * cooldown_repr(Cooldown *self);
static PyObject * cooldown___call__(Cooldown *self);
static int cooldown___bool__(Cooldown *self);
static PyObject * cooldown___int__(Cooldown *self);
static PyObject * cooldown___float__(Cooldown *self);
static PyObject * cooldown___iter__(PyObject *o);
static PyObject * cooldown___next__(Cooldown *self);
static PyObject * cooldown_richcompare(PyObject *o1, PyObject *o2, int op);
static PyObject * cooldown_cold(Cooldown *self);
static PyObject * cooldown_hot(Cooldown *self);
static PyObject * cooldown_reset(Cooldown *self, PyObject *args, PyObject *kwargs);
static PyObject * cooldown_pause(Cooldown *self);
static PyObject * cooldown_start(Cooldown *self);
static PyObject * cooldown_is_paused(Cooldown *self);
static PyObject * cooldown_set_to(Cooldown *self, PyObject *const *args, Py_ssize_t nargs);
static PyObject * cooldown_set_cold(Cooldown *self);

/* Class attributes */
static PyObject * cooldown_getter_duration(Cooldown *self, void *closure);
static int cooldown_setter_duration(Cooldown *self, PyObject *val, void *closure);
static PyObject * cooldown_getter_wrap(Cooldown *self, void *closure);
static int cooldown_setter_wrap(Cooldown *self, PyObject *val, void *closure);
static PyObject * cooldown_getter_paused(Cooldown *self, void *closure);
static int cooldown_setter_paused(Cooldown *self, PyObject *val, void *closure);
static PyObject * cooldown_getter_temperature(Cooldown *self, void *closure);
static int cooldown_setter_temperature(Cooldown *self, PyObject *val, void *closure);
static PyObject * cooldown_getter_remaining_(Cooldown *self, void *closure);
static int cooldown_setter_remaining(Cooldown *self, PyObject *val, void *closure);
static PyObject *cooldown_getter_normalized(Cooldown *self);
static int cooldown_setter_normalized(Cooldown *self, PyObject *val, void *closure);

/* Module init */
PyMODINIT_FUNC PyInit__pgcooldown(void);


/*----------------------------------------------------------------------
     _     _           _ _                 
    | |__ (_)_ __   __| (_)_ __   __ _ ___ 
    | '_ \| | '_ \ / _` | | '_ \ / _` / __|
    | |_) | | | | | (_| | | | | | (_| \__ \
    |_.__/|_|_| |_|\__,_|_|_| |_|\__, |___/
				 |___/     
----------------------------------------------------------------------*/


/* Module level methods */
static PyMethodDef pgcooldown_methods[] = {
    {"lerp", (PyCFunction)pgcooldown_lerp, METH_FASTCALL, DOCSTRING_LERP},
    {"invlerp", (PyCFunction)pgcooldown_invlerp, METH_FASTCALL, DOCSTRING_LERP},
    {"remap", (PyCFunction)pgcooldown_remap, METH_FASTCALL, DOCSTRING_LERP},
    {NULL, NULL, 0, NULL},
};


/* Dunder methods */
static PyNumberMethods cooldown_as_number = {
    .nb_bool = (inquiry)cooldown___bool__,
    .nb_int = (unaryfunc)cooldown___int__,
    .nb_float = (unaryfunc)cooldown___float__,
};

/* Class level methods */
static PyMethodDef cooldown_methods_[] = {
    {"cold", (PyCFunction)cooldown_cold, METH_NOARGS, NULL},
    {"hot", (PyCFunction)cooldown_hot, METH_NOARGS, NULL},
    {"is_paused", (PyCFunction)cooldown_is_paused, METH_NOARGS, NULL},
    {"pause", (PyCFunction)cooldown_pause, METH_NOARGS, NULL},
    {"reset", (PyCFunction)cooldown_reset, METH_VARARGS | METH_KEYWORDS, NULL},
    {"set_cold", (PyCFunction)cooldown_set_cold, METH_NOARGS, NULL},
    {"set_to", (PyCFunction)cooldown_set_to, METH_FASTCALL, NULL},
    {"start", (PyCFunction)cooldown_start, METH_NOARGS, NULL},
    {NULL},
};


/* Properties */
static PyGetSetDef cooldown_getset_[] = {
    {"duration", (getter)cooldown_getter_duration, (setter)cooldown_setter_duration, NULL, NULL},
    {"normalized", (getter)cooldown_getter_normalized, (setter)cooldown_setter_normalized, NULL, NULL},
    {"paused", (getter)cooldown_getter_paused, (setter)cooldown_setter_paused, NULL, NULL},
    {"remaining", (getter)cooldown_getter_remaining_, (setter)cooldown_setter_remaining, NULL, NULL},
    {"temperature", (getter)cooldown_getter_temperature, (setter)cooldown_setter_temperature, NULL, NULL},
    {"wrap", (getter)cooldown_getter_wrap, (setter)cooldown_setter_wrap, NULL, NULL},
    {NULL},
};


static PyTypeObject cooldown_type = {
    .ob_base = PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "_pgcooldown.Cooldown",
    .tp_doc = DOCSTRING_COOLDOWN,
    .tp_basicsize = sizeof(Cooldown),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = cooldown_new,
    .tp_init = (initproc)cooldown___init__,
    .tp_repr = (reprfunc)cooldown_repr,
    .tp_call = (ternaryfunc)cooldown___call__,
    .tp_as_number = &cooldown_as_number,
    .tp_richcompare = (richcmpfunc)cooldown_richcompare,
    .tp_iter = (getiterfunc)cooldown___iter__,
    .tp_iternext = (iternextfunc)cooldown___next__,
    /* .tp_dealloc = (destructor)cooldown_dealloc, */
    /* .tp_members = cooldown_members, */
    .tp_methods = cooldown_methods_,
    .tp_getset = cooldown_getset_,
};


static PyModuleDef cooldown_module = {
    .m_base = PyModuleDef_HEAD_INIT,
    .m_name = "_pgcooldown",
    .m_doc = "The _pgcooldown module that contains the Cooldown class",
    .m_size = -1,
    .m_methods = pgcooldown_methods,
};


/*----------------------------------------------------------------------
	   _   _ _ _ _   _           
     _   _| |_(_) (_) |_(_) ___  ___ 
    | | | | __| | | | __| |/ _ \/ __|
    | |_| | |_| | | | |_| |  __/\__ \
     \__,_|\__|_|_|_|\__|_|\___||___/

----------------------------------------------------------------------*/

#define is_cooldown(o) (PyType_IsSubtype(Py_TYPE(o), &cooldown_type))

static void dump(char *msg, Cooldown *self) {
    printf("%s\n", msg);
    printf("    Cooldown object %p\n", self);
    printf("    t0: %f\n", timespec_to_double(&self->t0));
    printf("    duration: %f\n", self->duration);
    printf("    wrap: %d\n", self->wrap);
    printf("    paused: %d\n", self->paused);
    printf("    remaining_: %f\n", self->remaining_);
    printf("    temperature: %f\n", get_temperature(self));
}

static double lerp(double a, double b, double t) {
    return t * (b - a) + a;
}


static double invlerp(double a, double b, double v) {
    return (v - a) / (b - a);
}

static double remap(double a0, double a1, double b0, double b1, double v) {
    return lerp(b0, b1, invlerp(a0, a1, v));
}

                                 
static double timespec_to_double(struct timespec *t) {
    return t->tv_sec + t->tv_nsec / T_FRACTION_SCALE;
}


static void double_to_timespec(struct timespec *t, double val) {
    t->tv_sec = (time_t)val;
    t->tv_nsec = (long)((val - (int)val) * T_FRACTION_SCALE);
}


static double diff_timespec(struct timespec *t0, struct timespec *t1) {
    return t1->tv_sec - t0->tv_sec + (t1->tv_nsec - t0->tv_nsec) / T_FRACTION_SCALE;
}


static void substract_timespec(struct timespec *t0, struct timespec *t1) {
    t0->tv_sec -= t1->tv_sec;
    t0->tv_nsec -= t1->tv_nsec;
}


static double current_delta(struct timespec *t0) {
    struct timespec now;

    timespec_get(&now, TIME_UTC);

    return diff_timespec(t0, &now);
}


static double get_temperature(Cooldown *self) {
    return self->paused
	? self->remaining_
	: self->duration - current_delta(&self->t0);
}


static void set_temperature(Cooldown *self, double val) {
    struct timespec now, delta;

    if (self->paused) {
	self->remaining_ = val;
    } else {
	timespec_get(&now, TIME_UTC);
	double_to_timespec(&delta, self->duration - val);

	self->t0.tv_sec = now.tv_sec - delta.tv_sec;
	self->t0.tv_nsec = now.tv_nsec - delta.tv_nsec;
    }
}


static double get_remaining(Cooldown *self) {
    double temperature = get_temperature(self);
    return MAX(temperature, 0.0);
}


static void set_remaining(Cooldown *self, double val) {
    set_temperature(self, MAX(val, 0.0));
}


static int is_cold(Cooldown *self) {
    return get_temperature(self) <= 0.0;
}


static void set_cold(Cooldown *self, int val) {
    if (val) {
	set_temperature(self, 0.0);
    } else {
	set_temperature(self, self->duration);
    }
}


static void set_paused(Cooldown *self, int val) {
    if (val) {
	self->remaining_ = get_temperature(self);
	self->paused = 1;
    } else {
	self->paused = 0;
	set_temperature(self, self->remaining_);
	self->remaining_ = 0.0;
    }
}


/*----------------------------------------------------------------------
      __                  _   _                 
     / _|_   _ _ __   ___| |_(_) ___  _ __  ___ 
    | |_| | | | '_ \ / __| __| |/ _ \| '_ \/ __|
    |  _| |_| | | | | (__| |_| | (_) | | | \__ \
    |_|  \__,_|_| |_|\___|\__|_|\___/|_| |_|___/
                                            
----------------------------------------------------------------------*/

static PyObject *pgcooldown_lerp(PyObject *self, PyObject *const *args, Py_ssize_t nargs) {
    double a, b, t;

    if (nargs != 3)
	return NULL;

    a = PyFloat_AsDouble(args[0]);
    b = PyFloat_AsDouble(args[1]);
    t = PyFloat_AsDouble(args[2]);

    return PyFloat_FromDouble(lerp(a, b, t));
}

static PyObject *pgcooldown_invlerp(PyObject *self, PyObject *const *args, Py_ssize_t nargs) {
    double a, b, v;

    a = PyFloat_AsDouble(args[0]);
    b = PyFloat_AsDouble(args[1]);
    v = PyFloat_AsDouble(args[2]);

    return PyFloat_FromDouble(invlerp(a, b, v));
}

static PyObject *pgcooldown_remap(PyObject *self, PyObject *const *args, Py_ssize_t nargs) {
    double a0, a1, b0, b1, v;

    a0 = PyFloat_AsDouble(args[0]);
    a1 = PyFloat_AsDouble(args[1]);
    b0 = PyFloat_AsDouble(args[2]);
    b1 = PyFloat_AsDouble(args[3]);
    v = PyFloat_AsDouble(args[4]);

    return PyFloat_FromDouble(remap(a0, a1, b0, b1, v));
}

/*----------------------------------------------------------------------
	  _                     _       __ 
      ___| | __ _ ___ ___    __| | ___ / _|
     / __| |/ _` / __/ __|  / _` |/ _ \ |_ 
    | (__| | (_| \__ \__ \ | (_| |  __/  _|
     \___|_|\__,_|___/___/  \__,_|\___|_|  
                                       
----------------------------------------------------------------------*/


static PyObject * cooldown_new(PyTypeObject *type, PyObject *args, PyObject *kwargs) {
    Cooldown *self;

    self = (Cooldown *)type ->tp_alloc(type, 0);
    if (self != NULL) {
	/* Alloc members here if appropriate */
    }

    return (PyObject *)self;
}


static int cooldown___init__(Cooldown *self, PyObject *args, PyObject *kwargs) {
    static char *kwargslist[] = {"duration", "wrap", "cold", "paused", NULL};
    int cold = 0;
    int paused = 0;
    PyObject *duration_or_cooldown;
    Cooldown *source;

    if (!PyArg_ParseTupleAndKeywords(
		args, kwargs, "O|$ppp", kwargslist,
		&duration_or_cooldown, &self->wrap, &cold, &paused))
	return -1;

    if (is_cooldown(duration_or_cooldown)) {
	source = (Cooldown *)duration_or_cooldown;

	self->t0.tv_sec = source->t0.tv_sec;
	self->t0.tv_nsec = source->t0.tv_nsec;
	self->duration = source->duration;
	self->wrap = source->wrap;
	self->paused = source->paused;
	self->remaining_ = source->remaining_;
    } else {
	self->duration = PyFloat_AsDouble(duration_or_cooldown);

	/* Do this first, since otherwise the timer is already running */
	if (paused) set_paused(self, 1);
	set_temperature(self, self->duration);
	if (cold) set_cold(self, 1);
    }

    return 0;
}


static void cooldown_dealloc(Cooldown *self) {
    /* pass */
}


/*----------------------------------------------------------------------
      ____ _                     _                 _           
     / ___| | __ _ ___ ___    __| |_   _ _ __   __| | ___ _ __ 
    | |   | |/ _` / __/ __|  / _` | | | | '_ \ / _` |/ _ \ '__|
    | |___| | (_| \__ \__ \ | (_| | |_| | | | | (_| |  __/ |   
     \____|_|\__,_|___/___/  \__,_|\__,_|_| |_|\__,_|\___|_|   
                                                           
----------------------------------------------------------------------*/

static PyObject * cooldown_repr(Cooldown *self) {
    int cold = 0; /* FIXME */

    return PyUnicode_FromFormat(
	    "Cooldown(%S, wrap=%S, paused=%S) at %p",
	    PyFloat_FromDouble(self->duration),
	    self->wrap ? Py_True : Py_False,
	    self->paused ? Py_True : Py_False,
	    self);
}


static PyObject * cooldown___call__(Cooldown *self) {
    return PyFloat_FromDouble(get_remaining(self));
}


static int cooldown___bool__(Cooldown *self) {
    return !is_cold(self);
}


static PyObject * cooldown___int__(Cooldown *self) {
    return PyLong_FromDouble(get_temperature(self));
}

static PyObject * cooldown___float__(Cooldown *self) {
    return PyFloat_FromDouble(get_temperature(self));
}

static PyObject * cooldown___iter__(PyObject *o) {
    Py_INCREF(o);
    return o;
}

static PyObject * cooldown___next__(Cooldown *self) {
    double remaining = get_remaining(self);

    return remaining ? PyFloat_FromDouble(get_temperature(self)) : NULL;
}

#define VAL_OF(o) (is_cooldown(o) \
	? get_temperature((Cooldown *)o) \
	: PyFloat_AsDouble(o))

static PyObject * cooldown_richcompare(PyObject *o1, PyObject *o2, int op) {
    double temperature;
    double other;

    if (is_cooldown(o1)) {
	temperature = get_temperature((Cooldown *)o1);
	other = PyFloat_AsDouble(PyNumber_Float(o2));
    } else {
	temperature = get_temperature((Cooldown *)o2);
	other = PyFloat_AsDouble(PyNumber_Float(o1));
    }

    switch(op) {
	case Py_LT:
	    return PyBool_FromLong(temperature < other);
	    break;
	case Py_LE:
	    return PyBool_FromLong(temperature <= other);
	    break;
	case Py_EQ:
	    return PyBool_FromLong(temperature == other);
	    break;
	case Py_NE:
	    return PyBool_FromLong(temperature != other);
	    break;
	case Py_GT:
	    return PyBool_FromLong(temperature > other);
	    break;
	case Py_GE:
	    return PyBool_FromLong(temperature >= other);
	    break;
	default:
	    PyErr_SetString(PyExc_ValueError, "Can't convert object to number");
	    return NULL;
    }

}


/*----------------------------------------------------------------------
  ____ _                                _   _               _     
 / ___| | __ _ ___ ___   _ __ ___   ___| |_| |__   ___   __| |___ 
| |   | |/ _` / __/ __| | '_ ` _ \ / _ \ __| '_ \ / _ \ / _` / __|
| |___| | (_| \__ \__ \ | | | | | |  __/ |_| | | | (_) | (_| \__ \
 \____|_|\__,_|___/___/ |_| |_| |_|\___|\__|_| |_|\___/ \__,_|___/
                                                                  
----------------------------------------------------------------------*/

static PyObject * cooldown_cold(Cooldown *self) {
    if (is_cold(self))
	Py_RETURN_TRUE;
    else
	Py_RETURN_FALSE;
}


static PyObject * cooldown_hot(Cooldown *self) {
    if (is_cold(self))
	Py_RETURN_FALSE;
    else
	Py_RETURN_TRUE;
}


static PyObject * cooldown_reset(Cooldown *self, PyObject *args, PyObject *kwargs) {
    /* Note: Initial duration is the base for calculating the overflow, but
     * final duration must be set before applying the overflow.
     * See comments further down. */

    int wrap = self->wrap;
    double old_temperature, new_temperature;
    double new_duration = self->duration;

    static char *kwargslist[] = {"", "wrap", NULL};

    if (!PyArg_ParseTupleAndKeywords(
		args, kwargs, "|d$p", kwargslist,
		&new_duration, &wrap))
	return NULL;

    if (!wrap) {
	new_temperature = new_duration;
    } else {
	old_temperature = get_temperature(self);

	new_temperature = old_temperature > 0
	    ? new_duration
	    : fmod(old_temperature, new_duration) + new_duration;
    }

    /* Only now overwrite! */
    self->duration = new_duration;
    set_temperature(self, new_temperature);

    Py_INCREF(self);
    return (PyObject *)self;
}


static PyObject * cooldown_pause(Cooldown *self) {
    set_paused(self, 1);

    Py_INCREF(self);
    return (PyObject *)self;
}


static PyObject * cooldown_start(Cooldown *self) {
    set_paused(self, 0);

    Py_RETURN_NONE;
}


static PyObject * cooldown_is_paused(Cooldown *self) {
    if (self->paused)
	Py_RETURN_TRUE;
    else
	Py_RETURN_FALSE;
}


static PyObject * cooldown_set_to(Cooldown *self, PyObject *const *args, Py_ssize_t nargs) {
    if (nargs != 1)
	return NULL;

    double new = PyFloat_AsDouble(args[0]);
    if (new > self->duration) {
	PyErr_SetString(PyExc_ValueError, "value larger than duration, use reset() instead.");
	return NULL;
    }

    set_temperature(self, PyFloat_AsDouble(args[0]));

    Py_RETURN_NONE;
}


static PyObject * cooldown_set_cold(Cooldown *self) {
    set_cold(self, 1);

    Py_RETURN_NONE;
}


/*----------------------------------------------------------------------
	   _   _        _ _           _            
      __ _| |_| |_ _ __(_) |__  _   _| |_ ___  ___ 
     / _` | __| __| '__| | '_ \| | | | __/ _ \/ __|
    | (_| | |_| |_| |  | | |_) | |_| | ||  __/\__ \
     \__,_|\__|\__|_|  |_|_.__/ \__,_|\__\___||___/

----------------------------------------------------------------------*/

static PyObject * cooldown_getter_duration(Cooldown *self, void *closure) {
    return PyFloat_FromDouble(self->duration);
}


static int cooldown_setter_duration(Cooldown *self, PyObject *val, void *closure) {
    self->duration = PyFloat_AsDouble(val);

    return 0;
}


static PyObject * cooldown_getter_wrap(Cooldown *self, void *closure) {
    if (self->wrap)
	Py_RETURN_TRUE;
    else
	Py_RETURN_FALSE;
}


static int cooldown_setter_wrap(Cooldown *self, PyObject *val, void *closure) {
    self->wrap = PyObject_IsTrue(val);

    return 0;
}


static PyObject * cooldown_getter_paused(Cooldown *self, void *closure) {
    if (self->paused)
	Py_RETURN_TRUE;
    else
	Py_RETURN_FALSE;
}


static int cooldown_setter_paused(Cooldown *self, PyObject *val, void *closure) {
    set_paused(self, self->paused = PyObject_IsTrue(val));

    return 0;
}


static PyObject * cooldown_getter_temperature(Cooldown *self, void *closure) {
    return PyFloat_FromDouble(get_temperature(self));
}


static int cooldown_setter_temperature(Cooldown *self, PyObject *val, void *closure) {
    set_temperature(self, PyFloat_AsDouble(val));

    return 0;
}


static PyObject * cooldown_getter_remaining_(Cooldown *self, void *closure) {
    return PyFloat_FromDouble(get_remaining(self));
}


static int cooldown_setter_remaining(Cooldown *self, PyObject *val, void *closure) {
    set_temperature(self, PyFloat_AsDouble(val));

    return 0;
}


static PyObject *cooldown_getter_normalized(Cooldown *self) {
    return self->duration
	? PyFloat_FromDouble(1 - get_remaining(self) / self->duration)
	: PyFloat_FromDouble(0.0);
}


static int cooldown_setter_normalized(Cooldown *self, PyObject *val, void *closure) {
    set_temperature(self, self->duration * PyFloat_AsDouble(val));

    return 0;
}


/*----------------------------------------------------------------------
			 _       _      
     _ __ ___   ___   __| |_   _| | ___ 
    | '_ ` _ \ / _ \ / _` | | | | |/ _ \
    | | | | | | (_) | (_| | |_| | |  __/
    |_| |_| |_|\___/ \__,_|\__,_|_|\___|

----------------------------------------------------------------------*/

PyMODINIT_FUNC PyInit__pgcooldown(void) {
    PyObject *m;

    if (PyType_Ready(&cooldown_type) < 0)
	return NULL;

    m = PyModule_Create(&cooldown_module);
    if (m == NULL)
	return NULL;

    if (PyModule_AddObjectRef(m, "Cooldown", (PyObject *)&cooldown_type) < 0) {
	Py_DECREF(m);
	return NULL;
    }

    return m;
}
