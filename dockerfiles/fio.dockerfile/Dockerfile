
FROM registry.access.redhat.com/rhel7/rhel
RUN yum install -y fio && yum clean all
ENV output_dir=/tmp
ENV output_file=fio.run.txt
ENV data_dir=/tmp
ENV num_jobs=2
ENV fsz_mb=2
CMD fio --name=writetest --ioengine=sync --rw=write --direct=0 \
        --create_on_open=1 --end_fsync=1 --bs=128k \
        --directory=${data_dir} --filename_format=f.\$jobnum.\$filenum \
        --filesize=${fsz_mb}m --numjobs=${num_jobs} \
        --output=${output_dir}/${output_file} ; ls -l $data_dir

