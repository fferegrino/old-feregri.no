---
layout: post
language: en
original_url: https://dev.to/fferegrino/conditional-random-fields-in-python-sequence-labelling-part-4-5ei2
title: Conditional Random Fields in Python - Sequence labelling (part 4) 
date: 2020-01-14 13:00:00
tags: python, data-science, nlp
short_summary: A quick tour of python-crfsuite to perform sequence labelling.
---  

<small>This is the fourth post in my series *Sequence labelling in Python*, find the previous one here: [Extracting more features](https://dev.to/fferegrino/extracting-more-features-sequence-labelling-in-python-part-3-3389). **Get the code for this series on [GitHub](https://github.com/fferegrino/vuelax-crf)**.</small>

Once we have our dataset with all the features we want to include, as well as all the labels for our sequences; we can move on to the actual training of our algorithm. For this task, we'll be using the [`python-crfsuite`](https://python-crfsuite.readthedocs.io/en/latest/) package, so pip-install it (or use your favourite package manager to get it):

```shell
pip install python-crfsuite
```

Once installed, let's load our dataset:

```python
import pandas as pd
import string

features_labels = pd.read_csv("data/features-labels.csv")
features_labels = features_labels[~features_labels['label'].isna()]
features_labels.head()
```

We also need some helper functions that work on strings; you'll see how they are used a bit further down:

```python
punctuation = set(string.punctuation)

def is_punctuation(token):
    return token in punctuation

def is_numeric(token):
    try:
        float(token.replace(",", ""))
        return True
    except:
        return False
```

## Input to pycrfsuite

The inputs to the algorithm must follow a particular format, where each token has its features represented by key-value pairs, each token may also have different features based on different factors, like its position. The following function takes in a dataframe and returns the corresponding features that can be consumed by the training method of our algorithm:

```python
def featurise(sentence_frame, current_idx):
    current_token = sentence_frame.iloc[current_idx]
    token = current_token['token']
    position = current_token['position']
    token_count = current_token['token_count']
    pos = current_token['pos_tag']
    
    # Shared features across tokens
    features = {
            'bias': True,
            'word.lower': token.lower(),
            'word.istitle': token.istitle(),
            'word.isdigit': is_numeric(token),
            'word.ispunct': is_punctuation(token),
            'word.position':position,
            'word.token_count': token_count,
            'postag': pos, 
    }
    
    if current_idx > 0: # The word is not the first one...
        prev_token = sentence_frame.iloc[current_idx-1]['token']
        prev_pos = sentence_frame.iloc[current_idx-1]['pos_tag']
        features.update({
            '-1:word.lower': prev_token.lower(),
            '-1:word.istitle':prev_token.istitle(),
            '-1:word.isdigit': is_numeric(prev_token),
            '-1:word.ispunct': is_punctuation(prev_token),
            '-1:postag':prev_pos 
        })
    else:
        features['BOS'] = True
    
    if current_idx < len(sentence_frame) - 1: # The word is not the last one...
        next_token = sentence_frame.iloc[current_idx+1]['token']
        next_tag = sentence_frame.iloc[current_idx+1]['pos_tag']
        features.update({
            '+1:word.lower': next_token.lower(),
            '+1:word.istitle': next_token.istitle(),
            '+1:word.isdigit': is_numeric(next_token),
            '+1:word.ispunct': is_punctuation(next_token),
            '+1:postag': next_tag 
        })
    else:
        features['EOS'] = True
    
    return features

featurise(offer_0, 1)
```

By featurising the first token of the first offer we get the following:  

```text
{'bias': True,
 'word.lower': 'cun',
 'word.istitle': False,
 'word.isdigit': False,
 'word.ispunct': False,
 'word.position': 1,
 'word.token_count': 11,
 'postag': 'np00000',
 '-1:word.lower': '¡',
 '-1:word.istitle': False,
 '-1:word.isdigit': False,
 '-1:word.ispunct': False,
 '-1:postag': 'faa',
 '+1:word.lower': 'a',
 '+1:word.istitle': False,
 '+1:word.isdigit': False,
 '+1:word.ispunct': False,
 '+1:postag': 'sp000'}
```

As you can see, the features are represented in a dictionary, where the keys can be any dictionary key, but I chose to name them like that to make it easy to find where each particular value comes from.

Again, we need some functions to build the sentences back from the tokens:

```python
def featurize_sentence(sentence_frame):
    labels = list(sentence_frame['label'].values)
    features = [featurize(sentence_frame, i) for i in range(len(sentence_frame))]
    
    return features, labels

def rollup(dataset):
    sequences = []
    labels = []
    offers = dataset.groupby('offer_id')
    for name, group in offers:
        sqs, lbls = featurize_sentence(group)
        sequences.append(sqs)
        labels.append(lbls)

    return sequences, labels

all_sequences, all_labels = rollup(features_labels)
```

We now have in `all_sequences` and `all_labels` our features and their corresponding labels ready for training.

## Training

Pretty much like in any other supervised problem, we need to split our training dataset into two (preferably three) sets of data; we can use `train_test_split` for this: 

```python
from sklearn.model_selection import train_test_split

train_docs, test_docs, train_labels, test_labels = train_test_split(all_sequences, all_labels)

len(train_docs), len(test_docs)
```

## Creating a CRF  

Though one can use a *sklearn-like* interface to create, train and infer with python-crfsuite, I've decided to use the original package and do all "by hand". 

The first step is to create an object of the class `Trainer`; then we can set some parameters for the training phase, feel free to play with these, as they may improve the quality of the tagger. Finally, we need to pass in our training data into the algorithm, and we do that with the append method:

```python
import pycrfsuite

trainer = pycrfsuite.Trainer(verbose=False)
    
trainer.set_params({
    'c1': 1.0,   # coefficient for L1 penalty
    'c2': 1e-3,  # coefficient for L2 penalty
    'max_iterations': 200, 

    'feature.possible_transitions': True
})


# We are feeding our training set to the algorithm here.
for xseq, yseq in zip(train_docs, train_labels):
    trainer.append(xseq, yseq)
```

Finally, we call the method train, that will, at the same time, save the model to a file that we can then use to perform inferences in new sentences.

```python
trainer.train('model/vuelax-bad.crfsuite')
```

## Labelling "unseen" sequences

To perform sequence labelling on instances that our algorithm did not see during training it is necessary to use an object of the `Tagger` class, and then load our saved model into it by using the `open` method.

```python
crf_tagger = pycrfsuite.Tagger()
crf_tagger.open('model/vuelax-bad.crfsuite')
```

Remember that each one of the sentences needs to be processed and put in the format required for the tagger to work that means, have the same features we used for training. We already have this in our `test_docs`, and we can use them directly:

```python
predicted_tags = crf_tagger.tag(test_docs[2])
print("Predicted: ",predicted_tags)
print("Correct  : ",test_labels[2])
```

The result may show that in this specific instance the tagger made no errors:

```text
Predicted:  ['n', 'o', 's', 'd', 'd', 'n', 'p', 'n']
Correct  :  ['n', 'o', 's', 'd', 'd', 'n', 'p', 'n']
```

## Evaluating the tagger

Seeing our algorithm perform very well in a single example may not inform us that well, so let's look at the bigger picture and while there may be better ways to evaluate the performance of the tagger, we'll use the traditional tools of a classification problem:

```python
from sklearn.metrics import classification_report

all_true, all_pred = [], []

for i in range(len(test_docs)):
    all_true.extend(test_labels[i])
    all_pred.extend(crf_tagger.tag(test_docs[i]))

print(classification_report(all_true, all_pred))
```

Should give you a result similar to...

```text
              precision    recall  f1-score   support

           d       0.96      0.99      0.97        98
           f       1.00      1.00      1.00        10
           n       1.00      1.00      1.00       831
           o       1.00      1.00      1.00        80
           p       1.00      1.00      1.00        60
           s       1.00      1.00      1.00        60

    accuracy                           1.00      1139
   macro avg       0.99      1.00      1.00      1139
weighted avg       1.00      1.00      1.00      1139

```

Our algorithm performs very, very well.


It may seem like we are done here, but we still need to put everything together, in an attempt to make it easier for us to tag new offers outside of our training and testing sets, we'll do that in my next post [putting everything together](https://dev.to/fferegrino/putting-everything-together-sequence-labelling-in-python-part-5-19ng).

As always, feel free to ask some questions if you have them by leaving a comment here or contacting me on twitter via [@io_exception](https://twitter.com/io_exception).