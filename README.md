# VCF Inspector

how to run VCF Inspector?

**directly**:
`python VCF_Inspector.py`

**docker**:
1.  create docker image
        `docker build -t vcf_inspector .`
2. create docker container
         `docker run -it --rm -p 8080:8080 -v /diskmnt/Projects/Users/chen.xiangyu/dash:/diskmnt/Projects/Users/chen.xiangyu/dash --name vcf_inspector vcf_inspector`
3. in docker container, run
        `python VCF_Inspector.py`

# vcf_inspector
