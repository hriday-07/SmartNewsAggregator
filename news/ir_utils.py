# news/ir_utils.py
import re
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from .models import Article
 

class InvertedIndex:
    def __init__(self):
        self.index = {}  # term -> list of article IDs
        self.stemmer = PorterStemmer()
        self.stopwords = set(stopwords.words('english'))
        self.build_index()
    
    def preprocess_text(self, text):
        """Tokenize, remove stopwords, and stem text"""
        if not text:
            return []
        # Lowercase and tokenize
        tokens = word_tokenize(text.lower())
        # Remove stopwords and stem
        tokens = [self.stemmer.stem(token) for token in tokens 
                 if token.isalnum() and token not in self.stopwords]
        return tokens
    
    def build_index(self):
        """Build inverted index from all articles in database"""
        # Get all articles
        articles = Article.objects.all()
        
        # Process each article
        for article in articles:
            # Combine title and content for better retrieval
            text = f"{article.title} {article.content}"
            
            # Get tokens
            tokens = self.preprocess_text(text)
            
            # Add each token to the index
            for token in set(tokens):  # Use set to count each term only once per document
                if token not in self.index:
                    self.index[token] = []
                if article.id not in self.index[token]:
                    self.index[token].append(article.id)
                    
    def parse_boolean_query(self, query_string):
        """Parse a Boolean query into a list of terms and operators"""
        # Replace operators with spaces around them for easier tokenization
        query_string = query_string.replace('AND', ' AND ')
        query_string = query_string.replace('OR', ' OR ')
        query_string = query_string.replace('NOT', ' NOT ')
        
        tokens = query_string.split()
        return tokens

    

# Add this function outside the class
def get_articles_from_ids(article_ids):
    """Retrieve Article objects from a list of IDs"""
    return Article.objects.filter(id__in=article_ids)

def boolean_search(self, query_string):
        """
        Process a Boolean query and return matching article IDs
        Supports AND, OR, NOT operators (case sensitive)
        """
        if not query_string or not self.index:
            return []
        
        tokens = inverted_index.parse_boolean_query(query_string)
        
        # Process NOT operators first
        i = 0
        while i < len(tokens):
            if tokens[i] == 'NOT' and i + 1 < len(tokens):
                # Get all document IDs
                all_docs = set()
                for docs in self.index.values():
                    all_docs.update(docs)
                
                # Get documents containing the term
                term = self.stemmer.stem(tokens[i+1].lower())
                term_docs = set(self.index.get(term, []))
                
                # Replace NOT term with complement
                tokens[i:i+2] = [list(all_docs - term_docs)]
            else:
                i += 1
        
        # Process each term and AND/OR operators
        result = []
        current_op = "OR"  # Default operator
        
        for token in tokens:
            if token == 'AND':
                current_op = 'AND'
            elif token == 'OR':
                current_op = 'OR'
            else:
                # Token is a term or already processed result
                if isinstance(token, list):
                    term_docs = token
                else:
                    # Get stemmed term
                    term = self.stemmer.stem(token.lower())
                    term_docs = self.index.get(term, [])
                
                if not result:
                    result = term_docs
                elif current_op == 'AND':
                    result = list(set(result) & set(term_docs))
                elif current_op == 'OR':
                    result = list(set(result) | set(term_docs))
        
        return result
