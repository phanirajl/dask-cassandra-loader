#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for the dask_cassandra_loader module.
"""
import pytest
import pandas as pd

from cassandra.cluster import Cluster
from cassandra.protocol import NumpyProtocolHandler
from cassandra.auth import PlainTextAuthProvider
from dask_cassandra_loader import PagedResultHandler
from cassandra.policies import RoundRobinPolicy


def test_cassandra_connection():
    auth = PlainTextAuthProvider(username='cassandra', password='cassandra')
    keyspace = 'dev'
    clusters = ['127.0.0.1']

    cluster = Cluster(clusters, auth_provider=auth, load_balancing_policy=RoundRobinPolicy())
    session = cluster.connect(keyspace)

    def pandas_factory(colnames, rows):
        return pd.DataFrame(rows, columns=colnames)

    session.client_protocol_handler = NumpyProtocolHandler
    session.row_factory = pandas_factory

    sql_query = 'SELECT title from play WHERE code = 1'

    future = session.execute_async(str(sql_query))
    handler = PagedResultHandler(future)
    handler.finished_event.wait()

    table_df = handler.df

    session.shutdown()
    if table_df.empty:
        raise AssertionError()
    else:
        if table_df['title'][0] == "hello!":
            print("It works!!!")
        else:
            raise AssertionError()

    return


def test_with_error():
    with pytest.raises(ValueError):
        # Do something that raises a ValueError
        raise(ValueError)


# Fixture example
@pytest.fixture
def an_object():
    return {}


def test_dask_cassandra_loader(an_object):
    if an_object != {}:
        raise AssertionError()
