# Import required libraries
from mrjob.job import MRJob
import re
import json
from collections import defaultdict
from mrjob.step import MRStep

class ChiSquareJob(MRJob):

    # Configure command line arguments to accept stopwords and category file paths
    def configure_args(self):
        super(ChiSquareJob, self).configure_args()
        self.add_file_arg('--stopwords', help='Path to the stopwords file')
        self.add_file_arg('--category', help='Path to the category file')

    # Load stopwords from a file
    def load_stopwords(self):
        with open(self.options.stopwords, 'r') as f:
            return set(word.strip() for word in f.readlines())

    # Load category counts from a file
    def load_category_counts(self, filename):
        category_counts = {}

        with open(filename, 'r') as f:
            for line in f:
                category, count = line.strip().split()
                category = category.strip('"')
                category_counts[category] = int(count)
        return category_counts

    # Initialize the mapper with stopwords and tokenizer regex
    def mapper_init_1(self):
        self.stopwords = self.load_stopwords()
        self.tokenizer = re.compile(r'[\s\d\(\)\[\]\{\}\.,!?\-,;:+\=_"\'`~#@&*%€$§\\/]+')

    # Initialize the reducer with category counts and total documents count
    def reducer_init_1(self):
        self.category_counts_dict = self.load_category_counts("category_counts.txt")
        self.N = sum(self.category_counts_dict.values())

    # Mapper function: Tokenize, case fold, filter stopwords and single-character tokens, and emit unique tokens
    def mapper_1(self, _, line):
        review = json.loads(line)
        review_text = review['reviewText']
        category = review['category']

        # Preprocessing steps:
        # 1. Tokenization
        tokens = self.tokenizer.split(review_text)

        # 2. Case folding
        tokens = [token.lower() for token in tokens]

        # 3. Stopword filtering, filtering tokens with only one character, and removing duplicates
        unique_tokens = set(token for token in tokens if token not in self.stopwords and len(token) > 1)

        # Yield one key-value pair for each unique token
        for token in unique_tokens:
            yield token, (category, 1)

    # Combiner function: Combine counts for the same token and category
    def combiner_1(self, key, values):
        token = key
        reviews_per_cat_per_term = defaultdict(int)

        for category, count in values:
            reviews_per_cat_per_term[category] += count

        for category, count in reviews_per_cat_per_term.items():
            yield token, (category, count)

    # Reducer function: Calculate Chi-squared statistic for each token-category pair
    def reducer_1(self, key, values):
        token = key
        reviews_per_cat_per_term = defaultdict(int)
        total_word_documents = 0

        # Accumulate counts of token occurrences per category
        for category, count in values:
            reviews_per_cat_per_term[category] += count
            total_word_documents += count

        # Calculate Chi-squared statistic for each token-category pair
        for category in reviews_per_cat_per_term:

            CAT = self.category_counts_dict[category]

            A = reviews_per_cat_per_term[category]
            B = total_word_documents - A
            C = CAT - A
            D = self.N - A - B - C

            upper_part = self.N*(A*D - B*C)**2
            lower_part = (A + B)*(A + C)*(B + D)*(C + D)
            chi_squared = upper_part/lower_part

            # Emit category and token with its Chi-squared value
            yield category, (token, chi_squared)

    # Mapper function for the second step: Pass category and token with its Chi-squared value
    def mapper_2(self, key, values):
        yield key, values

    # Reducer function for the second step: Select top 75 terms with highest Chi-squared values per category
    def reducer_2(self, key, values):
        top_n = 75
        category = key
        top_terms = sorted(values, key=lambda x: x[1], reverse=True)[:top_n]
        terms_and_chi_squared = [(term, chi_squared) for term, chi_squared in top_terms]
        yield category, terms_and_chi_squared

    # Mapper function for the third step: Emit category and terms with their Chi-squared values
    def mapper_3(self, key, values):
        category = key
        terms_and_chi_squared = values
        yield None, (category, terms_and_chi_squared)

    # Reducer function for the third step: Generate final output with sorted categories and merged dictionary
    def reducer_3(self, _, values):
        sorted_categories = sorted(values, key=lambda x: x[0])

        all_terms = set()
        for category, terms_and_chi_squared in sorted_categories:
            terms_line = " ".join([f"{term}:{chi_squared}" for term, chi_squared in terms_and_chi_squared])
            yield category, terms_line
            all_terms.update(term for term, _ in terms_and_chi_squared)

        # Emit merged dictionary with all unique terms sorted
        merged_dict_line = " ".join(sorted(all_terms))
        yield "MergedDict", merged_dict_line

    # Define MapReduce steps
    def steps(self):
        return [
            MRStep(mapper_init=self.mapper_init_1,
                   mapper=self.mapper_1,
                   combiner=self.combiner_1,
                   reducer_init=self.reducer_init_1,
                   reducer=self.reducer_1),
            MRStep(mapper=self.mapper_2,
                   reducer=self.reducer_2),
            MRStep(mapper=self.mapper_3,
                   reducer=self.reducer_3)
        ]

# Run the ChiSquareJob
if __name__ == '__main__':
    ChiSquareJob.run()

