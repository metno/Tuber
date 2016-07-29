# Tuber
Connector for various message queues

## Getting started
### Installing 
* git clone https://github.com/metno/Tuber.git
* cd Tuber
* python setup.py install

optionally: bash run_tests.sh

### Configuring
Tuber will reads its setup from a configuration file in traditional 'ini-format'. Where each endpoint is described in a separate section.

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

The first section, `[myQueue:input]`, specifies how the Tuber instance identified as myQueue will receive messages. Here it will listen on port 16000 on all local interfaces for a TCP connection as described in WMO-No. 386 part II.

The next section, `[myQueue:output]`, tells Tuber where it should put the messages it receives. In this case it will connect to a Kafka cluster and publish to the topic myQueue.

### Running
Start tuber by running `tuber myQueue`.

Any errors encountered during startup will be printed to STDERR and syslog. Tuber will then only log to syslog.
