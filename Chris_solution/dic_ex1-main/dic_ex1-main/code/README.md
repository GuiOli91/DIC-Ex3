# DIC - Project 1: Text Retrieval with Hadoop (Group 43)
This is the solution of Group 43 to Project 1 of the course 194.048 Data-intensive Computing in 2023S.

## Code

### Run

If you want to run the code with the combined dataset use: 

```python
bash run_mapreduce.sh hdfs:///user/dic23_shared/amazon-reviews/full/reviewscombined.json
```

If you want to run the code with the devset use: 

```python
bash run_mapreduce.sh hdfs:///user/dic23_shared/amazon-reviews/full/reviews_devset.json
```

Alternatively, you can the following commands respectively: 

```python
bash run_mapreduce.sh combined
bash run_mapreduce.sh devset
```
