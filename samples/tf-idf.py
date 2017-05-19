#tf-idf法のコード
#sentence　のところに好きな文を入力すると、tf-idf値が検出される

#例　
##sentence = ["私は猫である","猫は犬と私が好きだ","私が佐藤だ"]
##1 で 0.21972245773362198
##1 ある 0.21972245773362198
##1 は 0.08109302162163289
##1 猫 0.08109302162163289
##1 私 0.0
##2 犬 0.13732653608351372
##2 と 0.13732653608351372
##2 好き 0.13732653608351372
##2 猫 0.05068313851352055
##2 は 0.05068313851352055
##という感じ



import MeCab
import math

sentence = ["私は猫である","猫は犬と私が好きだ","私が佐藤だ"]

num = len(sentence)
result = []

for i in range(num):
    tagger = MeCab.Tagger()
    result.append(tagger.parse(sentence[i]))


wordCount = {}
allCount = {}
sub_tfstore = {}
tfcounter = {}
tfstore = {}
sub_idf = {}
idfstore = {}
merge_idf = {}
tfidf = {}
merge_tfidf = {}
wordList = []
sum = 0

for i in range(num):
    wordList.append(result[i].split()[:-1:2])

for i in range(num):
    for word in wordList[i]:
        allCount[i] = wordCount.setdefault(word,0)
        wordCount[word]+=1
    allCount[i] = wordCount
    wordCount = {}

for i in range(num):
    for word in allCount[i]:
        sum = sum + allCount[i][word]
    sub_tfstore[i] = sum
    sum = 0

for i in range(num):
    for word in allCount[i]:
        tfcounter[word] = allCount[i][word]*1.0/sub_tfstore[i]
    tfstore[i] = tfcounter
    tfcounter = {}

for i in range(num):
    for word in wordList[i]:
        wordCount.setdefault(word,0)
    for word in allCount[i]:
        wordCount[word] += 1
    sub_idf = wordCount

for i in range(num):
    for word in allCount[i]:
        idfstore[word] = math.log(1.0*math.fabs(num)/math.fabs(sub_idf[word]))
    merge_idf[i] = idfstore
    idfstore = {}

for i in range(num):
    for word in allCount[i]:
        tfidf[word] = tfstore[i][word]*merge_idf[i][word]
    merge_tfidf[i] = tfidf
    tfidf = {}

for i in range(num):
    for word,count in sorted(merge_tfidf[i].items(),key = lambda x:x[1],reverse = True):
        print (i+1,word,count)
