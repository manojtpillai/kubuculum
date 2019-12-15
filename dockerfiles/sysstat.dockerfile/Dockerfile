
FROM registry.access.redhat.com/rhel7/rhel
RUN yum install -y sysstat && yum clean all
ENV output_dir=/tmp
ENV output_file=sar.txt
ENV mon_interval=10
ENV mon_count=30
CMD sar -n DEV -BdpqruW $mon_interval $mon_count | tee ${output_dir}/${output_file}

