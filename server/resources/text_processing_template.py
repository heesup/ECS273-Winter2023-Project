import re
from nltk.stem import WordNetLemmatizer, PorterStemmer, SnowballStemmer
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# NOTE: current directory: ECS273-Winter2023/Assignment/Vue-Flask-Template/dashboard

################### @Author: Xiaoyu Zhang ################
################### Input type: string ###################
###################        Example     ################### 
# test_sentence = "this is a sentence to demonstrate how the preprocessing function works...!"
# preprocess(test_sentence)
##########################################################
def preprocess(raw_text: str) -> str:
    stop_words_file = '../server/data/SmartStoplist.txt'
    # load stop_words dictionary
    stop_words = []
    with open(stop_words_file, "r") as f:
        for line in f:
            stop_words.extend(line.split()) 

    # Step 1: remove non-letter characters and convert the string to lower case 
    letters_only_text: str = re.sub("[^a-zA-Z]", " ", raw_text)
    letters_only_text: str = letters_only_text.lower()

    # Step 2: tokenization -- split into words -> convert string into list ( 'hello world' -> ['hello', 'world'])
    words: list[str] = letters_only_text.split()

    # Step 3: remove stopwords
    cleaned_words = []
    for word in words:
        if word not in stop_words:
            cleaned_words.append(word)
    
    # Step 4: stemm or lemmatise words
    stemmed_words = []
    lemmatizer = PorterStemmer() #plug in here any other stemmer or lemmatiser you want to try out
    for word in cleaned_words:
        word = lemmatizer.stem(word)   #dont forget to change stem to lemmatize if you are using a lemmatizer
        stemmed_words.append(word)
    
    # Step 5: converting list back to string and return
    return " ".join(stemmed_words)

###################    @Author: Xiaoyu Zhang   ###################
################### Input type: list of string ###################
###################           Example          ################### 
# test_sentence = "tim burton alic wonderland anticip movi year good mention hardcor lewi carrol fan find disappoint movi base book featur charact coupl locat stori complet alic longer girl unconvent young woman dream find wonderland night day real life arriv expect alic suppos save inhabit evil red queen reign back kind sister white queen meant knight shine armor figur speak"
# ShowWordCloud(test_sentence.split())
##################################################################
def ShowWordCloud(word_list: list[str]):
    all_words = " ".join(word_list)

    wordcloud = WordCloud(width = 700, height = 700, 
                    background_color ='white', 
                    min_font_size = 10).generate(all_words) 
    
    # plot the WordCloud image                        
    plt.figure(figsize = (5, 5), facecolor = None) 
    plt.imshow(wordcloud) 
    plt.axis("off") 
    plt.tight_layout(pad = 0) 
    
    plt.show()


