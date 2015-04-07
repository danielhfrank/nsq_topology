#!/usr/bin/env python

import json
import re
import sys  # noqa
import argparse

import requests
from toolz import reduceby, valmap


class NSQData(object):

    def __init__(self, nsqlookupd_addr, hostname_regex):
        self.nsqlookupd_addr = nsqlookupd_addr
        self._compiled_hostname_re = re.compile(hostname_regex)

    def match_hostname(self, hostname):
        return self._compiled_hostname_re.match(hostname).groups()[0]

    def get_nodes(self):
        return requests.get(self.nsqlookupd_addr + '/nodes').json()['data']['producers']

    def get_stats_dict(self, node):
        """
        Given node as dict from `get_nodes`, return dict {topic: {channel: set(host_class)}}
        """
        node_addr = "http://%s:%d" % (node['broadcast_address'], node['http_port'])
        topics = requests.get(node_addr + "/stats?format=json").json()['data']['topics']
        return dict((t['topic_name'], self.mk_channel_consumer_dict(t)) for t in topics)

    def mk_channel_consumer_dict(self, topic_data):
        def gen():
            for chan in topic_data['channels']:
                consumer_host_classes = set(self.match_hostname(cli['hostname'])
                                            for cli in chan['clients'])
                yield (chan['channel_name'], consumer_host_classes)
        return dict(gen())

    def get_stats_by_host_class(self):
        nodes = self.get_nodes()
        nodes_by_class = reduceby(
            lambda node: self.match_hostname(node['hostname']), lambda x, y: x, nodes)
        return dict((host_class, self.get_stats_dict(sample_host))
                    for host_class, sample_host in nodes_by_class.items())


def to_jsonable(obj):
    if isinstance(obj, set):
        return list(obj)
    assert isinstance(obj, dict)
    assert all(isinstance(k, (str, unicode)) for k in obj)
    return valmap(to_jsonable, obj)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--nsqlookupd-addr', default='http://localhost:4161')
    parser.add_argument('--hostname-regex', default=r'([^\.\d]+)\d*\..*')
    args = parser.parse_args()
    data = NSQData(args.nsqlookupd_addr, args.hostname_regex)
    stats = data.get_stats_by_host_class()
    print json.dumps(to_jsonable(stats))
