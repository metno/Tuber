# Tuber
Tuber transports WMO-bulletins between message systems. Currently WMO message switches as described in [WMO-No. 386](http://wis.wmo.int/file=2229) and [Kafka](http://kafka.apache.org/) is supported.

There is no routing component in Tuber and all messages that are received are immediately forwarded to the destination system. The only messages that are not forwarded are those that are obviously invalid (e.g. it is a duplicate or it has no AHL).

Tuber will do its best to reconnect if it the connection to an endpoint is lost.

## Getting started
### Installing 
* git clone https://github.com/metno/Tuber.git
* cd Tuber
* python setup.py install

optionally: bash run_tests.sh

### Configuring
Tuber reads its setup from a configuration file in traditional 'ini-format'. Where each endpoint is described in a separate section.

A simple example is presented below.
```ini
[myQueue:input]
type=gts
bind=0.0.0.0:16000

[myQueue:output]
type=kafka
bootstrap_servers=1.2.3.4:9092,5.6.7.8:9092
topic=myQueue
```

Section names contains both a Tuber instance id (e.g. `myQueue`) and a direction (either `input` or `output`). This makes it possible to configure several Tuber instances using a single setup file.

The first section, `[myQueue:input]`, specifies how the Tuber instance identified as myQueue will receive messages. Here it will listen on port 16000 on all local interfaces for a TCP connection from a WMO message switch.

The next section, `[myQueue:output]`, tells Tuber where it should put the messages it receives. In this case it will connect to a Kafka cluster and publish to the topic myQueue.

The available configuration settings are described in one of the following sections.

### Running
Start Tuber by running `tuber myQueue`.

Any errors encountered during startup will be printed to STDERR and syslog. Tuber will then only log to syslog.

## Configuration settings

**For all connection types**
 * `type` - Specifies connection type or protocol for this connection. Valid values: `kafka`, `gts` and `null` (Which does nothing. Useful for debugging and testing).

**For type=gts**
  * `bind` - Address and port to listen on if this is an input endpoint.
  * `connect` - Address and port to connect to if this is an output endpoint.

**For type=kafka**
  * `bootstrap_servers` - Comma separated list of servers that can be connected to in order to retrieve metadata about the Kafka cluster.
  * `topic` - Topic to subscribe or publish to.
  * All other settings are passed when instantiating producer and consumer objects from [kafka-python](http://kafka-python.readthedocs.io/en/master/index.html).
