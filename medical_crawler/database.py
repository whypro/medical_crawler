# -*- coding: utf-8 -*-

from pymongo import MongoClient

# MongoDB settings
MONGODB = {
    'Host': 'localhost',
    'Port': 27017,
    'Username': '',
    'Password': '',
}


def mongo_connect():
    client = MongoClient(MONGODB['Host'], MONGODB['Port'], tz_aware=True)
    return client

def mongo_close(client):
    client.close()

