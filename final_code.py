import json
from collections import OrderedDict
import pandas as pd
import numpy as np
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.tag import pos_tag
import re
import os
from gensim.models import Word2Vec
import keras
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from keras.utils import np_utils
from keras.optimizers import SGD
from keras.models import Sequential
from keras.layers import Dense, Activation, Flatten, Dropout, Conv1D, MaxPooling1D, Embedding
from keras.layers.embeddings import Embedding
from keras.initializers import Constant
from keras.models import load_model
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.model_selection import train_test_split



#Restaurant business id 뽑기
categolist = ['Food', 'Restaurants', 'Desserts', 'Burgers']
business_id_list = []
with open('/content/drive/My Drive/project_graduate/dataset/전처리 전 json/business.json', 'r', encoding='UTF-8') as uf:
  for line in uf:
    lineobj = json.loads(line)
    category = lineobj['categories']
    if category is None:
      continue
    elif categolist[0] in category:
      business_id_list.append(lineobj['business_id'])
      continue
    elif categolist[1] in category:
      business_id_list.append(lineobj['business_id'])
      continue
    elif categolist[2] in category:
      business_id_list.append(lineobj['business_id'])
      continue
    elif categolist[3] in category:
      business_id_list.append(lineobj['business_id'])
      continue
    else:
      continue
uf.close()

#가장 많은 리뷰를 가진 유저 뽑기
unique_userlist=[]
userid=[]
userreviewcount=[]
with open('/content/drive/My Drive/Z두번째 지난 플젝_지역별 평점 분석/yelp dataset/review.json', 'r', encoding='UTF-8') as f:
  for line in f:
    lineobj = json.loads(line)
    userid.append(lineobj['user_id'])
unique_userlist = set(userid)
for user in unique_userlist:
  tmp=[]
  cnt = userid.count(user)
  if cnt > 1000:
    tmp.append(user)
    tmp.append(cnt)
    userreviewcount.append(tmp)
    print(user, ' : ', cnt)
dfuser = pd.DataFrame(userreviewcount)
dfuser.columns = ['user_id', 'review_count']
dfuser.sort_values(by='review_count')
print(dfuser)

# 윗 코드를 돌려서 나온 review_count 중 가장 높은 값을 가지는 user_id를 직접 사용.
file_data = OrderedDict()
def data_to_json(data) :
    if type(data) is str : # 타입이 문자열이라면
        return '"' + data + '"' # 문자열을 "로 묶어주고
    elif type(data) is list : # 타입이 리스트라면
        return list_to_json(data, data_to_json) # 함수 호출
    elif type(data) is int or type(data) is float : # 타입이 숫자라면
        return data.__str__() # 그대로 반환
    elif type(data) is dict : # 타입이 dict라면
        return dict_to_json(data, data_to_json) # 함수 호출
    else :
        print("type은 {}".format(type(data)))
        return '""'
def list_to_json(list, func):
    out_str = "[" # [(대괄호)를 연다
    for val in list:
        out_str += func(val)
        out_str += ", " # ,(쉼표)로 데이터를 구분
    if len(out_str) > 2:
        out_str = out_str[:-2]
    out_str += "]" # ](대괄호)를 닫는다
    return out_str
def dict_to_json(dict, func) :
    out_str = "{" # {(중괄호)를 연다
    for key in dict.keys() :
        out_str += ('"' + key.__str__() + '"') # 키 값에 "(큰 따옴표)를 씌운다
        out_str += ": " # :(콜론)으로 Key와 Value를 분리
        out_str += func(dict[key])
        out_str += ", " # ,(쉼표)로 쌍과 쌍을 분리
    if len(out_str) > 2:
        out_str = out_str[:-2]
    out_str += "}" # }(중괄호)를 닫는다
    return out_str
with open('/content/drive/My Drive/dataset/yelp json/user_review_all.json', 'a', -1, encoding='UTF-8') as f:
  with open('/content/drive/My Drive/dataset/yelp json/review.json', 'r', encoding='UTF-8') as mf:
    for line in mf:
      lineobj = json.loads(line)
      if lineobj['user_id'] == 'CxDOIDnH8gp9KXzpBHJYXw':
        file_data['business_id'] = lineobj['business_id']
        file_data['stars'] = lineobj['stars']
        file_data['text'] = lineobj['text']
        f.write(dict_to_json(file_data, data_to_json))
        f.write('\n')
mf.close()
f.close()
with open('/content/drive/My Drive/dataset/yelp json/user_review_restaurant.json', 'a', -1, encoding='UTF-8') as f:
  with open('/content/drive/My Drive/dataset/yelp json/user_review_all.json', 'r', encoding='UTF-8') as mf:
    for line in mf:
      lineobj = json.loads(line)
      if lineobj['business_id'] in business_id_list:
        file_data['business_id'] = lineobj['business_id']
        file_data['stars'] = lineobj['stars']
        file_data['text'] = lineobj['text']

        f.write(dict_to_json(file_data, data_to_json))
        f.write('\n')
mf.close()
f.close()
with open('/content/drive/My Drive/dataset/yelp json/user_review_15.json', 'a', -1, encoding='UTF-8') as f:
  with open('/content/drive/My Drive/dataset/yelp json/user_review_restaurant.json', 'r', encoding='UTF-8') as mf:
    for line in mf:
      lineobj = json.loads(line)
      if lineobj['stars'] == 1 or lineobj['stars'] == 5:
        file_data['business_id'] = lineobj['business_id']
        file_data['stars'] = lineobj['stars']
        file_data['text'] = lineobj['text']

        f.write(dict_to_json(file_data, data_to_json))
        f.write('\n')
mf.close()
f.close()
# [데이터 추출 완료]

n=WordNetLemmatizer()
tx1 = ''
tx2 = ''
remove_list = ['NN', 'IN', 'DT', 'MD', 'TO', 'PR', 'CC', 'WD', 'WP']
with open('/content/drive/My Drive/pretrained/user_review_15.json', 'rt', encoding='UTF-8') as f:
    for line in f:
        lineobj = json.loads(line)
        tx1 = lineobj['text']
        tx3 = tx1.lower()
        word_tokens = word_tokenize(tx3)
        result = []
        words = []
        tag_l = pos_tag(word_tokens)
        for w in tag_l:
          if w[1][:2] in remove_list:
            continue
          else:
            words.append(w[0])
        stop_words = set(stopwords.words('english'))
        stop_words.update(['\'re', '\'d', '\'t', '\'ll', '\'ve', '\'s','\'m', '!', '.', ',', '/', '?', '\"', '@', '%', '&', '*', '=','(',')','{','}', '-', '--', 'u', '...','$', '#', '*', '@', ':', ';', '[',']','~'])
        stop_words.remove('not')
        for w in words:
          if w == 'n\'t':
            w = 'not'
          if w not in stop_words:
            a = re.sub('[^a-zA-Z ]', '', w)
            if a != '':
              result.append(a) #result에 불용어 제거된 tokens 존재
        newresult=[]
        for token in result:
          shortword = re.compile(r'\W*\b\w{1,2}\b')
          tk = shortword.sub('', token)
          if tk != '':
            newresult.append(tk)
        tmpresult=[]
        for review in newresult:
          if review[:3] != 'www':
            tmpresult.append(review)
        newresult = tmpresult
        notremove = ['unpretentious', 'unfortunately', 'approximately', 'complimentary', 'uncomfortable','disappointing']
        lenreview = []
        for review in newresult:
          if len(review) >= 13 and review not in notremove :
            continue
          else:
            lenreview.append(review)
        newresult = lenreview
        with open('/content/drive/My Drive/remove_only.txt', 'a', encoding='UTF-8') as mf:
          mf.write('[\n')
          mf.write('\n'.join(newresult))
          mf.write('\n]\n')
f.close()

labelAll = []
with open('/content/drive/My Drive/pretrained/user_review_15.json', 'rt', encoding='UTF-8') as f:
    for line in f:
        lineobj = json.loads(line)
        star = lineobj['stars']
        if star == 1 :
          labelAll.append(0)
        elif star == 5:
          labelAll.append(1)
f.close()
label = np.array(labelAll)
label = np_utils.to_categorical(label, num_classes=2)
result = []
dataAll2 = []
with open('/content/drive/My Drive/remove_only.txt', 'rt', encoding='UTF-8') as mf:
  while True:
    temp = mf.readline()
    if not temp:
      break
    if temp == '[\n':
      continue
    elif temp == ']\n':
      dataAll2.append(result)
      result = []
      continue
    else:
      l = len(temp)
      word = temp[0:l-1]
      result.append(word)
mf.close()
print('label size : ', len(label))
print('data size : ', len(dataAll2))

#word2vec 모델 생성
embedding_dim = 300
embedding_model = Word2Vec(sentences=dataAll2, size=embedding_dim, min_count=2, window=4, iter=200, workers=4, sg=1)
# load model
filename = '/content/drive/My Drive/pretrained/GoogleNews-vectors-negative300.bin'
embedding_model.intersect_word2vec_format(filename, binary=True)
# save model
filename = '/content/drive/My Drive/w2v_model_intersect_remove_15_final.txt'
embedding_model.wv.save_word2vec_format(filename, binary=False)

# load pretrained model
embeddings_index = {}
file = open(os.path.join('', '/content/drive/My Drive/w2v_model_intersect_remove_15_final.txt'), encoding="utf-8")
for line in file:
  values = line.split()
  word = values[0]
  coefs = np.asarray(values[1:])
  embeddings_index[word] = coefs
file.close()

# 전체 데이터 학습(6):검증(1):테스트(3)
# Stratified하게 트레이닝셋과 테스트셋으로 나눈다(1회만 실시)
seed = 777
dataAll2 = np.array(dataAll2)
train_index, test_index = train_test_split(np.array(range(dataAll2.shape[0])), shuffle=True, stratify=label, test_size=0.3, random_state=seed)
x_train, X_test = dataAll2[train_index], dataAll2[test_index]
y_train, Y_test = label[train_index], label[test_index]
train_index, valid_index = train_test_split(np.array(range(x_train.shape[0])), shuffle=True, stratify=y_train, test_size=0.1, random_state=seed)
X_train, X_valid = x_train[train_index], x_train[valid_index]
Y_train, Y_valid = y_train[train_index], y_train[valid_index]

# max_length - train data
train_sum=0
train_count = len(X_train)
for sent in X_train :
  train_sum = train_sum+len(sent)
test_count = len(X_test)
for sent in X_test :
  train_sum = train_sum+len(sent)
valid_count = len(X_valid)
for sent in X_test :
  train_sum = train_sum+len(sent)
MAX = train_sum / (train_count + test_count + valid_count)
MAX = int(MAX)
print(MAX)
tmp_train=[]
for review in X_train:
  if len(review) > 49: #MAX = 49
    tmp_train.append(review[0:50])
  else:
    tmp_train.append(review)
X_train = tmp_train
tmp_test=[]
for review in X_test:
  if len(review) > 49:
    tmp_test.append(review[0:50])
  else:
    tmp_test.append(review)
X_test = tmp_test
tmp_valid=[]
for review in X_valid:
  if len(review) > 49:
    tmp_valid.append(review[0:50])
  else:
    tmp_valid.append(review)
X_valid = tmp_valid

tokenizer_obj = Tokenizer()
tokenizer_obj.fit_on_texts(dataAll2)
sequences_obj = tokenizer_obj.texts_to_sequences(dataAll2)
word_index = tokenizer_obj.word_index
num_words = len(word_index)+1
embedding_dim = 300
embedding_matrix = np.zeros((num_words, embedding_dim))
for word, i in word_index.items():
  if i > num_words:
    continue
  embedding_vector = embeddings_index.get(word)
  if embedding_vector is not None :
    embedding_matrix[i] = embedding_vector
# vec - train data
tokenizer_obj_train = Tokenizer()
tokenizer_obj_train.fit_on_texts(X_train)
sequences_train = tokenizer_obj_train.texts_to_sequences(X_train)
# vec - test data
tokenizer_obj_test = Tokenizer()
tokenizer_obj_test.fit_on_texts(X_test)
sequences_test = tokenizer_obj_test.texts_to_sequences(X_test)
# vec - valid data
tokenizer_obj_valid = Tokenizer()
tokenizer_obj_valid.fit_on_texts(X_valid)
sequences_valid = tokenizer_obj_valid.texts_to_sequences(X_valid)
# pad_sequences_train
word_index_train = tokenizer_obj_train.word_index
print('Found %s unique tokens.' % len(word_index_train))
review_pad_train = pad_sequences(sequences_train, maxlen=MAX, padding = 'post')         # test data max가 더 커서 그 값으로 train, test 둘다 패딩
sentiment_train = Y_train
print('Shape of review tensor:', review_pad_train.shape)
print('Shape of sentiment tensor:', sentiment_train.shape)
num_words_train = len(word_index_train)+1
embedding_dim = 300
embedding_matrix_train = np.zeros((num_words_train, embedding_dim))
for word, i in word_index_train.items():
  if i > num_words_train:
    continue
  embedding_vector = embeddings_index.get(word)
  if embedding_vector is not None :
    embedding_matrix_train[i] = embedding_vector
print('train data word size : ',num_words_train)
# pad_sequences_test
word_index_test = tokenizer_obj_test.word_index
print('Found %s unique tokens(test).' % len(word_index_test))
review_pad_test = pad_sequences(sequences_test, maxlen=MAX, padding = 'post')   # test data max가 더 커서 그 값으로 train, test 둘다 패딩
sentiment_test = Y_test
print('Shape of review tensor(test):', review_pad_test.shape)
print('Shape of sentiment tensor(test):', sentiment_test.shape)
num_words_test = len(word_index_test)+1
embedding_matrix_test = np.zeros((num_words_test, embedding_dim))
for word, i in word_index_test.items():
  if i > num_words_test:
    continue
  embedding_vector = embeddings_index.get(word)
  if embedding_vector is not None :
    embedding_matrix_test[i] = embedding_vector
print('test data word size : ',num_words_test)
# pad_sequences_valid
word_index_valid = tokenizer_obj_valid.word_index
print('Found %s unique tokens(valid).' % len(word_index_valid))
review_pad_valid = pad_sequences(sequences_valid, maxlen=MAX, padding = 'post')   # test data max가 더 커서 그 값으로 train, test 둘다 패딩
sentiment_valid = Y_valid
print('Shape of review tensor(valid):', review_pad_valid.shape)
print('Shape of sentiment tensor(valid):', sentiment_valid.shape)
num_words_valid = len(word_index_valid)+1
embedding_matrix_valid = np.zeros((num_words_valid, embedding_dim))
for word, i in word_index_valid.items():
  if i > num_words_valid:
    continue
  embedding_vector = embeddings_index.get(word)
  if embedding_vector is not None :
    embedding_matrix_valid[i] = embedding_vector
print('valid data word size : ',num_words_valid)

model = Sequential()
model.add(Embedding(num_words, embedding_dim, embeddings_initializer=Constant(embedding_matrix), input_length=MAX, trainable = False))    #test data max length로 맞춤
model.add(Conv1D(filters=16, kernel_size=3, activation='relu'))
model.add(MaxPooling1D(pool_size=2))
model.add(Conv1D(filters=16 , kernel_size=2, activation='relu'))
model.add(MaxPooling1D(pool_size=2))
model.add(Conv1D(filters=32, kernel_size=2, activation='relu'))
model.add(Dropout(0.4))
model.add(Flatten())
model.add(Dense(128, activation='relu'))
model.add(Dense(64, activation='relu'))
model.add(Dense(2, activation='sigmoid'))
sgd = SGD(lr=0.01, nesterov=True, decay=1e-6, momentum=0.9)
model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
print(model.summary())

result = model.fit(review_pad_train, sentiment_train, batch_size=6, epochs=30, validation_data=(review_pad_valid, sentiment_valid), verbose=1)
loss, accuracy = model.evaluate(review_pad_test, sentiment_test, batch_size=6, verbose=1)
print('Accuracy: %f' % (accuracy*100))

model.save('/content/drive/My Drive/final/111_%.2f.h5' % (accuracy*100))

model = load_model('/content/drive/My Drive/final/model1_85.29.h5') #load the model
yhat = model.predict_classes(review_pad_test)
wrongpre=[]
for i in range(len(review_pad_test)):
    ans = sentiment_test[i]
    pre = yhat[i]
    if ans[0]==1:
      print("bad review")
    else:
        print("good review")
