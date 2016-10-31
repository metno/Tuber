# Tuber
Tuber transports WMO-bulletins between message systems. Currently WMO message switches, as described in [WMO-No. 386](http://wis.wmo.int/file=2229), and [Kafka](http://kafka.apache.org/) is supported.

Each Tuber instance is responsible for forwarding messages from a single input source to a single output destination. This means that Tuber is not a traditinal message switch, which generally has several destination endpoints and that makes a routing desicion for each message, but is more accurately described as a forwarder or an adapter. 

Messages that are obviously invalid or that are duplicates are discarded. Tuber will do its best to reconnect if it the connection to an endpoint is lost.

## Getting started
### Installing 
* git clone https://github.com/metno/Tuber.git
* cd Tuber
* python setup.py install

optionally: bash run_tests.sh

### Configuring
Tuber reads its setup from a configuration file (default: `/etc/tuber.ini`) in traditional 'ini-format'. Where each endpoint is described in a separate section.

A simple example is presented below.
```ini
[myInstance:input]
type=gts
bind=0.0.0.0:16000

[myInstance:output]
type=kafka
bootstrap_servers=1.2.3.4:9092,5.6.7.8:9092
topic=myTopic
```
Each Tuber instance is assigned an instance id from the command line when it is started and section names contains both a Tuber instance id (e.g. `myInstance`) and a direction (either `input` or `output`). This makes it possible to configure several Tuber instances using a single setup file. 

The first section, `[myInstance:input]`, specifies how the Tuber instance identified as myInstance will receive messages. Here it will listen on port 16000 on all local interfaces for a TCP connection from a WMO message switch.

The next section, `[myInstance:output]`, tells Tuber where it should put the messages it receives. In this case it will connect to a Kafka cluster using one of the servers set in `bootstrap_servers` and publish to the topic myTopic.

The available configuration settings are described in one of the following sections.

### Running
Start Tuber by running `tuber myInstance`. If the configuration file named something other than `/etc/tuber.ini`, you need specify its location like this `tuber myInstance -c <filename>`.

Any errors encountered during startup will be printed to STDERR and syslog. Tuber will then only log to syslog.

## Configuration settings

**For all connection types**
 * `type` - Specifies connection type or protocol for this connection. Valid values: `kafka`, `gts` and `null` (Which does nothing and is only useful for debugging and testing).

**For type=gts**
  * `bind` - Address and port to listen on if this is an input endpoint.
  * `connect` - Address and port to connect to if this is an output endpoint.

**For type=kafka**
* `bootstrap_servers` - Comma separated list of servers that can be connected to in order to retrieve metadata about the Kafka cluster.
* `topic` - Topic to subscribe or publish to.
* `ssl_*` - same meaning as for [kafka-python](http://kafka-python.readthedocs.io/en/master/index.html)
* `sasl_*` - same meaning as for [kafka-python](http://kafka-python.readthedocs.io/en/master/index.html)
* `security_protocol` - same meaning as for [kafka-python](http://kafka-python.readthedocs.io/en/master/index.html)
