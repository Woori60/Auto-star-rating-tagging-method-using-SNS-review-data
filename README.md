# Auto star rating tagging method using SNS review data

A CNN model-based review auto-tagging technique that allows reviews to be automatically binary categorized as positive/negative for SNS review data written in natural language.

2 models : 
1) for personal star rating tagging (111 data)
2) for enterprise star rating tagging (4000 data)

Development Environment :
- python
- colab
- keras, tensorflow

System Architecture :
- review text data -> data preprocessing module -> word embeddinng (word2vec) -> convolutional neural network

Recommendation Technique:
- Used Data : Yelp Dataset (from - yelp.com)
  : 111 data for one person's review that the star is 1 or 5
  : 4000 data for multiple persons' review that the star is 1 or 5
  
- Data preprocessing
  : Tokenization -> Filter unnecessary PoS -> Normalization -> Cleaning (stop words etc)

- Word Embedding
  : train word2vec model 
    -> window size = 4, embedding dimension = 300, iteration = 200, Skip-gram

- Convolutional Neural Network
  : Look our poster!

Final Model:
[model 1] accuracy : 79%
[model 2] accuracy : 70%
  
