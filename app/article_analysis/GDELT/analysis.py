import spacy
from chopping_block.word import Word
from gensim import corpora, models, similarities, downloader
from gensim.models import Word2Vec
#from sentence_transformers import SentenceTransformer
#from sentence_transformers.util import cos_sim
nlp = spacy.load('en_core_web_trf')

# Example usage
long_text_1 = "This is a very long piece of text that needs to be broken down into smaller chunks for easier processing or analysis."
text_1 = Word(20,long_text_1)

long_text_2 = "This is also a very long piece of text that might need to be broken down into similarly small chunks for natural language processing."
text_2 = Word(20,long_text_2)

text_1.__iter_print__()
print("\n")
text_2.__iter_print__()

doc1 = nlp(text_1.get_text())
doc2 = nlp(text_2.get_text())

long_text_3 = "This is a test long piece of text that needs to be broken down into smaller chunks for easier processing or analysis."
text_3 = Word(20,long_text_3)

doc3 = nlp(text_3.get_text())

print(doc1.ents)


#https://radimrehurek.com/gensim/models/word2vec.html
#^ngram analysis, training


#res1=doc1.similarity(doc2)
#print(f"Doc 1 similarity to doc 2: \n" + str(res1) + "\n")
#res2 =doc1.similarity(doc3)
#print(f"Doc 1 similarity to doc 3: \n" + str(res2) + "\n")






#chunk_2 = chunk_text_field(long_text_2,long_text_1.get)


#consider linking corpus data to the concepts in the database. Perhaps, topic "fiance" is a financial article corpus, "tech" is a tech document corpus, etc
# Stream a training corpus directly from S3.
#corpus = corpora.MmCorpus("s3://path/to/corpus")

# Train Latent Semantic Indexing with 200D vectors.
#lsi = models.LsiModel(corpus, num_topics=200)

# Convert another corpus to the LSI space and index it.
#index = similarities.MatrixSimilarity(lsi[another_corpus])

# Compute similarity of a query vs indexed documents.
#sims = index[query]