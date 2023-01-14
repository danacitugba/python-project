'''
Setinment Classifier:

The task is to build a sentiment classifier, which will detect how positive or negative each tweet is. You will create a csv file, which contains columns for the Number of Retweets, Number of Replies, Positive Score (which is how many happy words are in the tweet), Negative Score (which is how many angry words are in the tweet), and the Net Score for each tweet. At the end, you upload the csv file to Excel or Google Sheets, and produce a graph of the Net Score vs Number of Retweets.
'''



punctuation_chars = ["'", '"', ",", ".", "!", ":", ";", '#', '@']
# lists of words to use
positive_words = []
# list that show positive words
with open("positive_words.txt") as pos_f:
    for lin in pos_f:
        if lin[0] != ';' and lin[0] != '\n':
            positive_words.append(lin.strip())

negative_words = []
# list that show negative words
with open("negative_words.txt") as pos_f:
    for lin in pos_f:
        if lin[0] != ';' and lin[0] != '\n':
            negative_words.append(lin.strip())


def strip_punctuation(string):
    # function that strips punctuation characters from the string
    # punctuation characters are listed in the list named punctuation_chars
    for i in punctuation_chars:
        while i in string:
            string = string.replace(i, "")
            continue
    return string


def get_pos(string):
    # functions that calculates the sum of positive words in the string
    # positive words are stored in the list named positive_words
    string_new = strip_punctuation(string.lower())
    liste_string = string_new.split()
    liste = []
    for word in positive_words:
        if word in liste_string:
            liste.append(word)
    return len(liste)


def get_neg(string):
    # functions that calculates the sum of negative words in the string
    # negative words are stored in the list named negative_words
    string_new = strip_punctuation(string.lower())
    liste_string = string_new.split()
    liste = []
    for word in negative_words:
        if word in liste_string:
            liste.append(word)
    return len(liste)


outfile2 = open("resulting_data.csv", "w")
outfile2.write("Number of Retweets, Number of Replies, Positive Score, Negative Score, Net Score")
outfile2.write('\n')

outfile = open("project_twitter_data.csv", "r")
twitler = outfile.readlines()
for twit in twitler[1:]:
    satir = twit.strip().split(',')
    a = get_pos(twit)
    b = get_neg(twit)
    c = a - b
    row_string = '{},{},{},{},{}'.format(satir[1], satir[2], str(a), str(b), str(c))
    outfile2.write(row_string)
    outfile2.write('\n')
outfile.close()
outfile2.close()

