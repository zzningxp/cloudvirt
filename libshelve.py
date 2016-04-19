#!/usr/bin/env python
import shelve

def create(datefile):
    try:
        db = shelve.open(datefile, 'c')
    finally:
        db.close()

def modify(datefile, key, value):
    try:
        db = shelve.open(datefile, 'w')
        db[key] = value
    finally:
        db.close()

def load(datefile):
    ret = {}
    try:
        db = shelve.open(datefile, 'w')
        ret.update(db)
    finally:
        db.close()
    return ret


