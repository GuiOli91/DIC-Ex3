#!/bin/bash

# Check if input parameter is provided
if [ -z "$1" ]
then
    echo "Please provide an input parameter: 'combined', 'devset' or full HDFS path"
    exit 1
fi

# Set the input file based on the parameter
if [[ $1 == "combined" || $1 == "devset" ]]
then
    suffix="combined"
    if [[ $1 == "devset" ]]; then suffix="_devset"; fi
    input_file="hdfs:///user/dic23_shared/amazon-reviews/full/reviews${suffix}.json"
else
    input_file=$1
fi

####### Part 1 ########

# Run the MapReduce job on Hadoop
python3 category_count_job.py --hadoop-streaming-jar /usr/lib/hadoop/tools/lib/hadoop-streaming-3.3.4.jar -r hadoop $input_file > category_counts.txt 

###### Part 2 #######

# Run the MapReduce job on Hadoop
python3 chi_square_job.py --hadoop-streaming-jar /usr/lib/hadoop/tools/lib/hadoop-streaming-3.3.4.jar -r hadoop $input_file --category category_counts.txt --stopwords stopwords.txt > result.txt
