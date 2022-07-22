FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update -y&&apt-get install vim -y

#COPY . .
RUN git clone https://github.com/Brave-banana/vcf_inspector.git

CMD [ "/bin/bash" ]