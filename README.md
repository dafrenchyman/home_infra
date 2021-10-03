# Home Infrastructure via Pulumi

Pulumi Kubernetes infra code to help in recreating a bunch of home services.

This could be used as a template for creating your own home Kubernetes home infra if desired.

I basically used this as an excuse to play around and migrate some (not all yet) of my `docker-compose ` services over to kubernetes.

I'm using [microk8s](https://microk8s.io/) on my home server and will try eventually try to figure out a way to get some remote [retroarch](https://www.retroarch.com/) server. I'm playing around with both trying the [emscripten](https://emscripten.org/) and also the really interesting [Games on Whales](https://artifacthub.io/packages/helm/k8s-at-home/games-on-whales).

# Setup for developement:

- Setup a python 3.x venv (usually in `.venv`)
  - You can run `./scripts/create-venv.sh` to generate one
- `pip3 install --upgrade pip`
- Install pip-tools `pip3 install pip-tools`
- Update dev requirements: `pip-compile --output-file=requirements.dev.txt requirements.dev.in`
- Update requirements: `pip-compile --output-file=requirements.txt requirements.in`
- Install dev requirements `pip3 install -r requirements.dev.txt`
- Install requirements `pip3 install -r requirements.txt`
- `pre-commit install`

## Update versions

`pip-compile --output-file=requirements.dev.txt requirements.dev.in --upgrade`

# Run `pre-commit` locally.

`pre-commit run --all-files`
