# Cretan, a Remote Logging Service

## Introduction

Cretan is a transport-generic message broker. You can use Cretan to bootstrap
communications between applications and devices with minimum development time.

Cretan provides a generic API that application developers can use to send
messages to any networked device using a variety of protocols and media.

Currently, the Cretan API only supports Python. There are plans in the future
to support Modern C++ and ES6. There is also a command line client (written in
Python 3) which can be used in a pinch to send messages from shell scripts.

## The Cretan Ecosystem

In Cretan, there are two communication elements: _services_ and _streams_.

### Services...

...are the means of communicating with the Cretan daemon. Clients select a
service from the API which must be provided by the daemon they wish to
communicate with. Currently, the only supported service is a Datagram service.

*Note*: The Datagram service does not support any kind of authentication or
authorization, and will forward any message from any host on the listening
interface as long as the packet is legible. In the future, it will be possible
to configure services that use authentication, but for the moment, take care
before exposing a Cretan daemon to the public internet. Always protect it
behind a firewall.

### Streams...

...are communication "channels" that originate at the Cretan daemon and
terminate at one or more devices or processes. Streams communicate using a
protocol over a mechanism. Users create and name streams which may terminate
anywhere--an app on an Android device, a process listening on a Unix socket,
an MQTT client, an IP multicast group, or anything you can think of. As long as
Cretan supports the mechanism, and the endpoint speaks the same protocol as the
stream, you can send messages to it.

Cretan is in development, and currently only supports a Discord mechanism,
which is used to communicate with Discord Guilds using the Discord API. In the
future, many mechanisms will be supported, such as:

* Other RESTful APIs
* HTTPS
* MQTT
* Firebase Cloud Messaging
* Email

## Installing

This repository is currently hosted on a private PyPI server. Once it has
reached a stable state, it may be uploaded to the central PyPI. To install
using pip, specify the index url:

```
pip install --user --index-url https://edtwardy.hopto.org:443/pypi cretan
```
