
FROM registry.access.redhat.com/rhel7/rhel
RUN yum install -y java-1.8.0-openjdk-devel && yum clean all
WORKDIR /ycsb
RUN curl -O --location https://github.com/brianfrankcooper/YCSB/releases/download/0.17.0/ycsb-0.17.0.tar.gz && tar xzf ycsb-0.17.0.tar.gz && mv ycsb-0.17.0 ycsb-latest && rm ycsb-0.17.0.tar.gz
