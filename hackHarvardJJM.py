import nltk
from nltk.tokenize import sent_tokenize
from nltk.sentiment.vader import SentimentIntensityAnalyzer

def get_cleaned_book(book):
    '''
    argument is the filename for the book not including .txt,
    returns a string with the entire text of the book
    '''
    book = 'books/' + book + '.txt'
    with open(book, 'r') as f:
        #lines is a list of all the sentences in the book
        lines = f.readlines()
        #specifying start and end of book
        book_lines = []
        appending = False
        for line in lines:
            if '*** START OF THE PROJECT GUTENBERG' in line:
                appending = True  
            if '*** END OF THE PROJECT GUTENBERG' in line:
                appending = False
            if appending:
                book_lines.append(line)
        
        cleaned_book = ' '.join(book_lines[1:])
                       
        return cleaned_book

def get_energy_positivity_score(book):
    '''
    takes text in as a string and returns the compound score
    for sentiment between 0 and 1
    '''   
    text = get_cleaned_book(book)

    #sentiment analysis to get compound score
    analyzer = SentimentIntensityAnalyzer()
    score = analyzer.polarity_scores(text) 

    
    final_score = (score['pos'] - score['neg'])
    return final_score*10
