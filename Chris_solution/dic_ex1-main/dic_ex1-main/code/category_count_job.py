import json
from mrjob.job import MRJob
from mrjob.protocol import JSONValueProtocol

class CategoryCountJob(MRJob):
    # Set the input protocol to JSONValueProtocol for automatic JSON parsing
    INPUT_PROTOCOL = JSONValueProtocol

    # Mapper function: Takes a JSON review object and yields the category with a count of 1
    def mapper(self, _, review):
        category = review['category']
        yield category, 1

    # Combiner function: Performs local aggregation on the mapper side
    # Sums up counts for each category, reducing the amount of data transferred to the reducer
    def combiner(self, category, counts):
        yield category, sum(counts)

    # Reducer function: Sums up the counts for each category and yields the result
    def reducer(self, category, counts):
        yield category, sum(counts)

if __name__ == '__main__':
    CategoryCountJob.run()