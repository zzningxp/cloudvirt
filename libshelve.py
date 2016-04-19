#!/usr/bin/env python
import shelve

def create(datefile):
    try:
        db = shelve.open(datefile, 'c')
    finally:
        db.close()

def modify(datefile, key, value):
    try:
        create(datefile)
        db = shelve.open(datefile, 'w')
        db[key] = value
    finally:
        db.close()

def load(datefile):
    ret = {}
    try:
        create(datefile)
        db = shelve.open(datefile, 'w')
        ret.update(db)
    finally:
        db.close()
    return ret

def iskeyexists(datefile, key):
    try:
        create(datefile)
        db = shelve.open(datefile, 'w')
        return db.has_key(key)
    finally:
        db.close()
    return False

def getkey(datefile, key):
    try:
        create(datefile)
        db = shelve.open(datefile, 'w')
        if db.has_key(key):
            return db[key]
        return None 
    finally:
        db.close()
    return None

def getkeys(datefile):
    try:
        create(datefile)
        db = shelve.open(datefile, 'w')
        return db.keys() 
    finally:
        db.close()
    return None


def delkey(datefile, key):
    try:
        create(datefile)
        db = shelve.open(datefile, 'w')
        if db.has_key(key):
            del db[key]
            return 0
        return 1
    finally:
        db.close()
    return 1
