import nltk
from nltk.tokenize import sent_tokenize
from nltk.sentiment.vader import SentimentIntensityAnalyzer

def get_energy_positivity_score(text):
    '''
    takes text in as a string and returns the compound score
    for sentiment between 0 and 1
    '''   
    #sentiment analysis to get compound score
    analyzer = SentimentIntensityAnalyzer()
    score = analyzer.polarity_scores(text)
    compound_score = score['compound']
    
    #since compound score is betweeen -1 and 1, normalising to
    #get a score between 0 and 1.
    final_score = (compound_score - (-1))/(1-(-1))
    

    return final_score