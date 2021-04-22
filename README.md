# Blockworkr

Cerntralized DNS blocklist (& whitelist) management. Deploy via Docker, Kubernetes, or python pip. 

### Why?

I manage several domain blocking tools across various sites; friends, family, businesses, etc. Seems I have
 accumulated quite a number of firewalls & pihole installs that I need to keep updated with proper blocklists. 
 There are plenty of quality blocklists available, but keeping the list of lists synced on each device is quite a 
 pain. And when something needs whitelisted, it usually needs whitelisted everywhere. This tool aims to provide a 
 means to simplify managing blocklists and whitelists on multiple devices. 
 
### What?

Simply put, given a list of blocklsts and whitelists, this tool will periodically combine, dedupe the blocklists 
 excluding any whitelisted items. This unified blocklist is then available via a webservice, allowing you to 
 replace all your block and white lists on all your piholes or firewalls with the one unified url served by this tool. 
 
### Deploying 

You'll need to create a `config.yaml` file (check repo for `example_config.yaml`) and place it at
 `/etc/blockworkr/config.yaml` for Blockworkr to find the file automatically. Alternatively you can provide 
 an environment variable `CONFIG_FILE` with the full path to a config file. 

#### Docker
Blockworkr is intended to be deployed via docker. You can find it on the docker hub at 
https://cloud.docker.com/repository/docker/zebpalmer/blockworkr. 

Blockworkr can be started with this docker run command:
 `docker run  -p 8080:80 -v /etc/blockworkr:/etc/blockworkr blockworkr:latest`
 this will make the resulting unified output available at `http://localhost:8080/unified.txt`. Make sure that the 
 config file is in the appropriate path as there is no default config for blockworkr. If the file is not present, 
 the container will fail. 
 
##### Docker Latest
Currently, we are only pushing a `latest` docker tag. This tag follows the `master` branch on git, so it may change 
quite fast. One the project matures a bit more, we'll tag a release version at which point latest will point to the 
most recent release. 

 
##### Multiple Configurations

You'll see in the example config file that Blockworkr supports multiple 'combinations'. Lets say that
 you want to serve a few sites one combination of blocklists, but another site needs a different combinations of lists, 
 you can assign each combination in the config file. Each combination of blocklists will be available
 under via it's name as defined in the config file. You'll notice the example config file has combinations `standard` 
 and `slim`. There's nothing special about these names, you can name your combinations whatever you want. In the example
 case, two urls will be available `/standard.txt` and `/slim.txt`. Blockworkr handles all the deduplication and
 whitelisting separately for each combination. Allowing you to put just the final combination url desire in your pihole
 or firewall configuation. The goal of this project is to give you one, single, url appropriate for any blocking device.
 

#### Service Start 

You should note that this service will return a 503 error on all endpoints when it does not have current data. 
 Specifically, on service startup, it will return 503 until the first update has completed. This is to prevent 
 an incomplete list from being served. I suggest using `/healthz` as a health endpoint if you are using a container 
 orchestrator (e.g. Docker swarm or Kubernetes), this will ensure traffic is not routed to a new instance until it
 is ready to provide data. The health endpoint (and any endpoint requiring data) will throw 503 again if the data is 
 older than double the frequency (default 24 hrs) 



### TODO

* Finalize API 
* CI/CD pushing docker images (once API is done-ish)
* Add output caching & optional centralized cache 

### Example Service 

The goal of this project is to make it simple for you to host your own custom unified blocklists, not to become 
 yet another blocklist. But, you're welcome to use my blockworkr deployment for testing, or even for real if
 you're happy with the list. But, I don't want to be a blocklist manager. If you want to add something to my custom
 unified blocklist, or whitelist something on it, you are welcome to submit a PR to the GitHub repo 
 [zebpalmer/dns_blocklists](https://github.com/zebpalmer/dns_blocklists) which is where I maintain my own lists. But 
 again, this project hopes enable you to deploy your own custom unified list. 
 
You can access the example service [here](https://blockworkr.halo.sh/lists/). I have two configurations running, 
[slim.txt](https://blockworkr.halo.sh/lists/slim.txt) and 
[standard.txt](https://blockworkr.halo.sh/lists/standard.txt). 


###### Disclaimer

I make no warranty about the example service. But... if it goes down, it'll be down for my managed devices too. :)     


### Feedback & PRs Welcome!

Feel free to open an issue for any questions, bugs, etc. Keep in mind this project just started and written in an 
an afternoon (Feb 12, 2019), so it's a bit rough around the edges. 

##### Blocklist Maintainer?

I mention elsewhere in this readme that I don't want to be a blocklist maintainer. But if you are, and you're
 considering using Blockworker to mix and match your blocklists, I'd love to get feedback and feature requests
 from your prospective. 


## Dev Setup

Start a memcached server in docker `docker network create blockworkr 
 && docker run --name memcached --network blockworkr -d memcached -m 256 --max-item-size=128M`

Then start the dev docker container with `--network blockworkr` and set config to use memcached server `memcached`
