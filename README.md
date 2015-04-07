# nsq_topology

This is a set of scripts to generate a graph of an NSQ topology, like so:

![topo](https://www.dropbox.com/s/mvitozg21ofk5d7/nsq_pgv_redacted.png?dl=1)

It has two components:

## nsq_data

This script builds up the data backing the topology graph. It does so by communicating
with nsqlookupd and then with all the nsqds in the cluster. It is likely that you will
want to run it on the same machines hosting nsqlookupd, which will have sufficient access
to communicate with the nsqd instances. At the very least, you'll want to run it somewhere
in your datacenter.

`nsq_data` can take a regex as an argument to extract a "host class" from a hostname.
For example, in the default configuration, it will extract the host class "nsqlookup"
from the hostname "nsqlookup01.tinyurl.com". Extracting this host class is essential
to coming up with a readable graph.

`nsq_data` depends on `requests` and `toolz`, which are both pip-installable.

It outputs data in json format, with the 'schema': `[{host_class: {topic: {channel: [host_class]}}}]`

## nsq_graph

This script takes the output of `nsq_data` and uses `pygraphviz` to generate a DOT graph
of your topology.

It can be loaded as a module and run with a custom function applied to
make the labels of the edges in the graph more readable (or to prune away some of them).

It depends on `pygraphviz` and in turn the `graphviz` library, which might
make it easier to run on your development machine.

Graphviz can write a variety of image formats; it will infer the desired format from the
extension of the provided output path

## Running nsq_topology

Putting the pieces together, you may wish to run the components like so:

```sh
 ssh nsqlookup01 "python /path/to/nsq_data.py" \
    | python nsq_graph.py --input - --output $OUTPUTFILE
```
