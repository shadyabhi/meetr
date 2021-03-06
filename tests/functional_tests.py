#!/usr/bin/env python

import unittest
import json
import urllib
import urllib2
import cql

class TestMeetr(unittest.TestCase):

    meetr_url = "http://localhost:8888/1.0/metrics"

    def execute_cql(cls, cql_str):
        cluster = 'localhost'
        keyspace = 'stats'
        port = 9160

        connection = cql.connect(cluster, port,  keyspace, cql_version='3.0.0')
        cursor = connection.cursor()
        cursor.execute(cql_str)
        
        rows = cursor.fetchall()
        cols = cursor.description

        cursor.close()
        connection.close()

        result = list()
        for row in rows:
            result_row = dict()
            for i in range(len(cols)):
                result_row[cols[i][0]] = row[i]
            result.append(result_row)

        return result

    def setUp(self):
        cql_str = "DELETE FROM metrics WHERE metric_id = 'test-metric';"
        self.execute_cql(cql_str)


    def test_single_insert(self):
        test_data = {
            'metric_id' : 'test-metric',
            'ts' : "2003-12-18 12:18:18+0530",
            'value' : 1
        }

        data = urllib.urlencode(test_data)
        res = urllib2.urlopen(self.meetr_url, data)
        self.assertEqual(res.getcode(), 200)

        cql_str = "SELECT * FROM metrics WHERE metric_id = 'test-metric';"
        rows = self.execute_cql(cql_str)
        self.assertEqual(len(rows), 1)

    def test_search(self):
        test_data = [
            {
                'metric_id' : 'test-metric',
                'ts' : "2003-12-18 12:18:18+0530",
                'value' : 1
            },
            {
                'metric_id' : 'test-metric',
                'ts' : "2003-12-18 12:18:19+0530",
                'value' : 1
            },
            {
                'metric_id' : 'test-metric',
                'ts' : "2003-12-18 12:18:20+0530",
                'value' : 1
            },
            {
                'metric_id' : 'test-metric',
                'ts' : "2003-12-18 12:18:21+0530",
                'value' : 1
            }
        ]

        for row in test_data:
            cql_template = """INSERT INTO metrics (
                metric_id, 
                ts,
                value
                ) VALUES ('{0}', '{1}', {2});"""
            cql_str = cql_template.format(row['metric_id'], row['ts'], row['value'])
            self.execute_cql(cql_str)

        data = urllib.urlencode((
            ('metric', 'test-metric'),
            ('from', "2003-12-18 12:18:18+0530"),
            ('to', "2003-12-18 12:18:21+0530"),
            ('aggregation', 'sum')
            ))

        res = urllib2.urlopen(self.meetr_url + '?' + data)
        result = json.load(res)

        self.assertEqual(result['value'], 4)
    

    def test_bulk_insert(self):
        test_data = [
            {
                'metric_id' : 'test-metric',
                'ts' : "2003-12-18 12:18:18+0530",
                'value' : 1
            },
            {
                'metric_id' : 'test-metric',
                'ts' : "2003-12-18 12:18:19+0530",
                'value' : 1
            },
            {
                'metric_id' : 'test-metric',
                'ts' : "2003-12-18 12:18:20+0530",
                'value' : 1
            },
            {
                'metric_id' : 'test-metric',
                'ts' : "2003-12-18 12:18:21+0530",
                'value' : 1
            }
        ]

        metrics = json.dumps(test_data)
        data = urllib.urlencode((('batch','True'),('metrics', metrics)))

        res = urllib2.urlopen(self.meetr_url, data)
        self.assertEqual(res.getcode(), 200)

        data = urllib.urlencode((
            ('metric', 'test-metric'),
            ('from', "2003-12-18 12:18:18+0530"),
            ('to', "2003-12-18 12:18:21+0530"),
            ('aggregation', 'sum')
            ))

        res = urllib2.urlopen(self.meetr_url + '?' + data)
        result = json.load(res)

        self.assertEqual(result['value'], 4)












if __name__ == '__main__':
    unittest.main()
