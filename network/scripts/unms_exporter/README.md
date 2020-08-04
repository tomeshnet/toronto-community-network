# unms_exporter.py

This script extracts info from the Ubiquiti Network Management System ([UNMS](https://unms.com/)), and runs an HTTP server that serves data [Prometheus](https://prometheus.io/) can work with. It came out of issue [#47](https://github.com/tomeshnet/toronto-community-network/issues/47).

It used to live as a Github gist, and it's history during that time can be seen [here](https://gist.github.com/makeworld-the-better-one/cec776797fae66195e68ccde265b7fa1/revisions).

## Usage
Run the server:
```
UNMS_KEY=foobar python3 unms_exporter.py
```
The `UNMS_HOST` environment variable is also available to be set, by default the script uses the value `unms.tomesh.net`.

By default it runs on port 8000, this can be changed in the script.

## Development

Update the `VERSION` variable for future changes.
