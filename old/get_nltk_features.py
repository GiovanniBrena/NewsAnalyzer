from nltk.tokenize import word_tokenize
import nltk
import json
import sys
import getopt

def get_feature(file_input, feature):
    data = json.loads(open(file_input).read())
    dict_tot = {}
    texts = {}
    for user in data:
        texts[user] = ""
        for t in data[user]:
            texts[user] += t['text'] + ". "

    for user in texts:
        text_tokenized = word_tokenize(texts[user])
        text_tagged = nltk.pos_tag(text_tokenized, tagset='universal')
        
        dict_freq = {}
        if feature == 'NOUN' or feature == 'VERB':
            word_tag_fd = nltk.FreqDist(word.lower() for (word, tag) in text_tagged if tag==feature)
            words = []
            for word in word_tag_fd:
                words.append((nltk.stem.WordNetLemmatizer().lemmatize(word.lower(), 'v'), word_tag_fd[word]))
            for word in words:
                if word[0].isalpha():
                    if word[0] not in dict_freq:
                        dict_freq[word[0]] = 0
                    dict_freq[word[0]] += word[1]

        elif feature == 'NNP':
            tagged_sent = nltk.pos_tag(text_tokenized)
            words = [word for word,pos in tagged_sent if pos == feature]
            for word in words:
                if word not in dict_freq:
                    dict_freq[word] = 0
                dict_freq[word] += 1

        dict_tot[user] = {}
        dict_tot[user][feature] = dict_freq
            
    return dict_tot


def save_feature(feature, file_output):
    j = json.dumps(feature)
    file = open(file_output,'w')
    file.write(j)

def main():
    
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'f:x:')
    except getopt.GetoptError as err:
        # print help information and exit:
        print('err')  # will print something like "option -a not recognized"
        #        usage()
        sys.exit(2)
    file_input = None
    for o, a in opts:
        if o == "-f":
            file_input = a
        if o == "-x":
            feature = a

    if feature == 'all':
        features = ['NOUN', 'VERB', 'NNP']
        for feat in features:
            users_features = get_feature(file_input+'.json', feat)
            file_output = file_input+'_'+feat
            save_feature(users_features, file_output+'.json')
    else:
        users_features = get_feature(file_input+'.json', feature)
        file_output = file_input+'_'+feature
        save_feature(users_features, file_output+'.json')

if __name__ == "__main__":
    main()
