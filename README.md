# VCF Inspector

how to run VCF Inspector?

**directly**:
First, install the libraries needed. See in requirements.txt
	```
	python VCF_Inspector.py
	```

**docker**:
1.  create docker image
	```
	docker build -t vcf_inspector .
	```
2. create docker container
	```
	docker run -it --rm -p 8080:8080 -v /diskmnt/Projects/Users/chen.xiangyu/dash:/diskmnt/Projects/Users/chen.xiangyu/dash --name vcf_inspector vcf_inspector
	```
3. in docker container, run
	```
	python VCF_Inspector.py
	```

**compute1**
1. git the code from github
	```
	git clone https://github.com/Brave-banana/vcf_inspector.git && cd vcf_inspector
	```
2. Set the `LSF_DOCKER_VOLUMES` environment variable to mount the location of  files
	```
	export LSF_DOCKER_VOLUMES="/storage1/fs1/dinglab/Active/:/storage1/fs1/dinglab/Active/ /storage1/fs1/m.wyczalkowski/Active/:/storage1/fs1/m.wyczalkowski/Active/"
	```
3. submit through `bsub` (Notoce that this step should under directory `vcf_inspector`)
	```
	LSF_DOCKER_PORTS="8080:8080" bsub -Is -R "select[port8080=1]" -q general-interactive -a 'docker(bravebanana/vcf_inspector)' /bin/bash
	```
4. Run vcf_inspector
	```
	python VCF_Inspector.py
	```
5. Access the host's 8080 port to use. The host's ip address will be displayed on the terminal. For example，address + port should be like:
	http://compute1-exec-187.compute.ris.wustl.edu:8080/

