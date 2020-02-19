---
layout: post
language: en
original_url: https://dev.to/fferegrino/extracting-more-features-sequence-labelling-in-python-part-3-3389
title: Extracting more features - Sequence labelling in Python (part 3) 
date: 2020-01-14 12:00:00
tags: python, data-science, nlp
short_summary: Our algorithm needs more than part of the speech to work well, so let us give it more stuff to work with.
---  

<small>This is the third post in my series *Sequence labelling in Python*, find the previous one here: [Part of speech tagging](https://dev.to/fferegrino/part-of-speech-tagging-sequence-labelling-in-python-part-2-4o66). **Get the code for this series on [GitHub](https://github.com/fferegrino/vuelax-crf)**.</small>

While having the POS tags is good and valuable information, it may not be enough to get valuable predictions for our task. However, we can provide our algorithm with more information;  such as the length of the token, the length of the sentence, the position within the sentence, whether the token is a number or all uppercase...

Some imports:  

```python
from vuelax.tokenisation import index_emoji_tokenize
import pandas as pd
import csv
```  

Starting from our already labelled dataset (remember I have a file called `data/to_label.csv`). The following are just a few helper functions to read and augment our dataset:

```python
labelled_data = pd.read_csv("data/to_label-done.csv")
labelled_data.head()
```

We need to create a helper function to read all the labelled offers from the previously created `labelled_data` dataframe:

```python
def read_whole_offers(dataset):
    current_offer = 0
    rows = []
    for _, row in dataset.iterrows():
        if row['offer_id'] != current_offer:
            yield rows
            current_offer = row['offer_id']
            rows = []
        rows.append(list(row.values))
    yield rows
            
offers = read_whole_offers(labelled_data)
offer_ids, tokens, positions, pos_tags, labels = zip(*next(offers))
print(offer_ids)
print(tokens)
print(positions)
print(pos_tags)
print(labels)
```

And here is the output from the first flight offer:  

```text
(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
('¡', 'CUN', 'a', 'Ámsterdam', '$', '8,960', '!', 'Sin', 'escala', 'en', 'EE.UU')
(0, 1, 5, 7, 17, 18, 23, 25, 29, 36, 39)
('faa', 'np00000', 'sp000', 'np00000', 'zm', 'dn0000', 'fat', 'sp000', 'nc0s000', 'sp000', 'np00000')
('n', 'o', 's', 'd', 'n', 'p', 'n', 'n', 'n', 'n', 'n')
```

## Building our training set  

The features I decided to augment the data with are the following:  

 - Lengths of each token
 - Length of the whole offer (counted in tokens)
 - The POS tag of the token to the left
 - The POS tag of the token to the right
 - Whether the token is uppercase or not

And this is the respective function to generate said features:

```python
def generate_more_features(tokens, pos_tags):
    lengths =  [len(l) for l in tokens]
    n_tokens =  [len(tokens) for l in tokens]
    augmented = ['<p>'] + list(pos_tags) + ['</p>']
    uppercase = [all([l.isupper() for l in token]) for token in tokens]
    return lengths, n_tokens, augmented[:len(tokens)], augmented[2:], uppercase

generate_more_features(tokens, pos_tags)
```

As an example output:

```text
([1, 3, 1, 9, 1, 5, 1, 3, 6, 2, 5],
 [11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11],
 ['<p>',
  'faa',
  'np00000',
  'sp000',
...
  'sp000',
  'nc0s000',
  'sp000'],
 ['np00000',
  'sp000',
...
  'nc0s000',
  'sp000',
  'np00000',
  '</p>'],
 [False, True, False, False, False, False, False, False, False, False, False])
```

Finally, we need to apply the function to all the offers in our dataset, and save these to a file, to keep them handy for the next task, you can read more about it here: [Training a CRF in Python](https://dev.to/fferegrino/conditional-random-fields-in-python-sequence-labelling-part-4-5ei2).

As always, feel free to ask some questions if you have them by leaving a comment here or contacting me on twitter via [@io_exception](https://twitter.com/io_exception).