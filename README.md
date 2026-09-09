# Drop

Drop is a simple self-hosted file sharing service for a trusted local network. It has no accounts or database. Each upload is stored under a random directory and receives an easy-to-read link such as `/d/quiet-maple-river`. The browser interface uses a responsive dark theme with static Flask templates and CSS.

## Docker

```sh
docker build -t drop .
docker run --rm -p 8080:8080 -v drop-data:/data drop
```

Open `http://<host-ip>:8080/` from a device on the LAN. Uploaded files survive container restarts in the `/data` volume. The container runs as an unprivileged user.

The Docker image includes the Flask templates and static assets required by the web interface. Rebuild the image after changing files in `templates/` or `static/`.

To make generated links use a LAN address or hostname:

```sh
docker run --rm -p 8080:8080 \
  -e DROP_PUBLIC_URL=http://192.168.1.20:8080 \
  -v "$PWD/data:/data" drop
```

## curl

```sh
curl -H 'Accept: application/json' \
  -F 'file=@photo.jpg' -F expiration=30m \
  http://192.168.1.20:8080/upload
curl -OJ http://192.168.1.20:8080/d/quiet-maple-river
```

Expiration values are `download` (the default, delete after a successful download), `5m`, `30m`, `2h`, and `forever`. The service intentionally has no authentication or encryption and should only be exposed to a trusted network.

## Development

```sh
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python -m unittest discover -s tests -v
```
