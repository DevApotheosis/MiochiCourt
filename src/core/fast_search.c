#include <Python.h>
#include <string.h>
#include <stdlib.h>
#include <stdbool.h>

typedef struct {
    char *id;
    char *title;
    char *content;
    char *category;
    int collected;
    int analyzed;
} Item;

typedef struct {
    Item *items;
    int count;
    int capacity;
} ItemArray;

static ItemArray laws = {NULL, 0, 0};
static ItemArray evidence = {NULL, 0, 0};

static PyObject *py_add_law(PyObject *self, PyObject *args) {
    const char *law_id, *title, *content, *category;
    
    if (!PyArg_ParseTuple(args, "ssss", &law_id, &title, &content, &category)) {
        return NULL;
    }
    
    if (laws.count >= laws.capacity) {
        laws.capacity = laws.capacity == 0 ? 64 : laws.capacity * 2;
        laws.items = realloc(laws.items, laws.capacity * sizeof(Item));
        if (!laws.items) {
            PyErr_SetString(PyExc_MemoryError, "Failed to allocate memory");
            return NULL;
        }
    }
    
    Item *item = &laws.items[laws.count++];
    item->id = strdup(law_id);
    item->title = strdup(title);
    item->content = strdup(content);
    item->category = strdup(category);
    item->collected = 0;
    item->analyzed = 0;
    
    Py_RETURN_NONE;
}

static PyObject *py_add_evidence(PyObject *self, PyObject *args) {
    const char *ev_id, *name, *ev_type, *description, *location;
    
    if (!PyArg_ParseTuple(args, "sssss", &ev_id, &name, &ev_type, &description, &location)) {
        return NULL;
    }
    
    if (evidence.count >= evidence.capacity) {
        evidence.capacity = evidence.capacity == 0 ? 64 : evidence.capacity * 2;
        evidence.items = realloc(evidence.items, evidence.capacity * sizeof(Item));
        if (!evidence.items) {
            PyErr_SetString(PyExc_MemoryError, "Failed to allocate memory");
            return NULL;
        }
    }
    
    Item *item = &evidence.items[evidence.count++];
    item->id = strdup(ev_id);
    item->title = strdup(name);
    item->content = strdup(description);
    item->category = strdup(location);
    item->collected = 0;
    item->analyzed = 0;
    
    Py_RETURN_NONE;
}

static PyObject *py_search_laws(PyObject *self, PyObject *args) {
    const char *keyword;
    
    if (!PyArg_ParseTuple(args, "s", &keyword)) {
        return NULL;
    }
    
    PyObject *result = PyList_New(0);
    if (!result) return NULL;
    
    for (size_t i = 0; i < (size_t)laws.count; i++) {
        Item *law = &laws.items[i];
        
        if (strstr(law->title, keyword) != NULL || strstr(law->content, keyword) != NULL) {
            PyObject *tuple = Py_BuildValue("(ssss)", law->id, law->title, law->content, law->category);
            if (!tuple) {
                Py_DECREF(result);
                return NULL;
            }
            PyList_Append(result, tuple);
            Py_DECREF(tuple);
        }
    }
    
    return result;
}

static PyObject *py_search_laws_case_insensitive(PyObject *self, PyObject *args) {
    const char *keyword;
    
    if (!PyArg_ParseTuple(args, "s", &keyword)) {
        return NULL;
    }
    
    PyObject *result = PyList_New(0);
    if (!result) return NULL;
    
    size_t keyword_len = strlen(keyword);
    
    for (size_t i = 0; i < laws.count; i++) {
        Item *law = &laws.items[i];
        
        bool found = false;
        
        char *title = law->title;
        while (*title) {
            const char *kw = keyword;
            char *tl = title;
            while (*kw && *tl && tolower((unsigned char)*kw) == tolower((unsigned char)*tl)) {
                kw++;
                tl++;
            }
            if (*kw == '\0') {
                found = true;
                break;
            }
            title++;
        }
        
        if (!found) {
            char *content = law->content;
            while (*content) {
                const char *kw = keyword;
                char *ct = content;
                while (*kw && *ct && tolower((unsigned char)*kw) == tolower((unsigned char)*ct)) {
                    kw++;
                    ct++;
                }
                if (*kw == '\0') {
                    found = true;
                    break;
                }
                content++;
            }
        }
        
        if (found) {
            PyObject *tuple = Py_BuildValue("(ssss)", law->id, law->title, law->content, law->category);
            if (!tuple) {
                Py_DECREF(result);
                return NULL;
            }
            PyList_Append(result, tuple);
            Py_DECREF(tuple);
        }
    }
    
    return result;
}

static PyObject *py_get_evidence_by_id(PyObject *self, PyObject *args) {
    const char *ev_id;
    
    if (!PyArg_ParseTuple(args, "s", &ev_id)) {
        return NULL;
    }
    
    for (int i = 0; i < evidence.count; i++) {
        if (strcmp(evidence.items[i].id, ev_id) == 0) {
            Item *ev = &evidence.items[i];
            return Py_BuildValue("(ssssii)", ev->id, ev->title, ev->content, 
                                ev->category, ev->collected, ev->analyzed);
        }
    }
    
    Py_RETURN_NONE;
}

static PyObject *py_collect_evidence(PyObject *self, PyObject *args) {
    const char *ev_id;
    
    if (!PyArg_ParseTuple(args, "s", &ev_id)) {
        return NULL;
    }
    
    for (int i = 0; i < evidence.count; i++) {
        if (strcmp(evidence.items[i].id, ev_id) == 0) {
            evidence.items[i].collected = 1;
            Py_RETURN_TRUE;
        }
    }
    
    Py_RETURN_FALSE;
}

static PyObject *py_get_collected_evidence(PyObject *self, PyObject *args) {
    PyObject *result = PyList_New(0);
    if (!result) return NULL;
    
    for (int i = 0; i < evidence.count; i++) {
        if (evidence.items[i].collected) {
            Item *ev = &evidence.items[i];
            PyObject *tuple = Py_BuildValue("(ssss)", ev->id, ev->title, ev->content, ev->category);
            if (!tuple) {
                Py_DECREF(result);
                return NULL;
            }
            PyList_Append(result, tuple);
            Py_DECREF(tuple);
        }
    }
    
    return result;
}

static PyObject *py_clear_laws(PyObject *self, PyObject *args) {
    for (int i = 0; i < laws.count; i++) {
        free(laws.items[i].id);
        free(laws.items[i].title);
        free(laws.items[i].content);
        free(laws.items[i].category);
    }
    free(laws.items);
    laws.items = NULL;
    laws.count = 0;
    laws.capacity = 0;
    Py_RETURN_NONE;
}

static PyObject *py_clear_evidence(PyObject *self, PyObject *args) {
    for (int i = 0; i < evidence.count; i++) {
        free(evidence.items[i].id);
        free(evidence.items[i].title);
        free(evidence.items[i].content);
        free(evidence.items[i].category);
    }
    free(evidence.items);
    evidence.items = NULL;
    evidence.count = 0;
    evidence.capacity = 0;
    Py_RETURN_NONE;
}

static PyObject *py_get_law_count(PyObject *self, PyObject *args) {
    return PyLong_FromLong(laws.count);
}

static PyObject *py_get_evidence_count(PyObject *self, PyObject *args) {
    return PyLong_FromLong(evidence.count);
}

static PyMethodDef FastSearchMethods[] = {
    {"add_law", py_add_law, METH_VARARGS, "Add a law to the search index"},
    {"add_evidence", py_add_evidence, METH_VARARGS, "Add evidence to the manager"},
    {"search_laws", py_search_laws, METH_VARARGS, "Search laws by keyword (case sensitive)"},
    {"search_laws_case_insensitive", py_search_laws_case_insensitive, METH_VARARGS, "Search laws by keyword (case insensitive)"},
    {"get_evidence_by_id", py_get_evidence_by_id, METH_VARARGS, "Get evidence by ID"},
    {"collect_evidence", py_collect_evidence, METH_VARARGS, "Mark evidence as collected"},
    {"get_collected_evidence", py_get_collected_evidence, METH_VARARGS, "Get all collected evidence"},
    {"clear_laws", py_clear_laws, METH_NOARGS, "Clear all laws"},
    {"clear_evidence", py_clear_evidence, METH_NOARGS, "Clear all evidence"},
    {"get_law_count", py_get_law_count, METH_NOARGS, "Get law count"},
    {"get_evidence_count", py_get_evidence_count, METH_NOARGS, "Get evidence count"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef fast_search_module = {
    PyModuleDef_HEAD_INIT,
    "fast_search",
    "Fast search and evidence management module",
    -1,
    FastSearchMethods
};

PyMODINIT_FUNC PyInit_fast_search(void) {
    return PyModule_Create(&fast_search_module);
}