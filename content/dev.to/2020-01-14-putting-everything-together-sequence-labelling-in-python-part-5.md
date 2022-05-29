---
layout: post
language: en
original_url: https://dev.to/fferegrino/putting-everything-together-sequence-labelling-in-python-part-5-19ng
title: Putting everything together - Sequence labelling in Python (part 5) 
date: 2020-01-14 14:00:00
tags: python, data-science, nlp
short_summary: Let's prepare our algorithm pipeline for new flight offers.
---  

<small>This is the fifth (and last) post in my series *Sequence labelling in Python*, find the previous one here: [CRFs for sequence labelling](https://dev.to/fferegrino/conditional-random-fields-in-python-sequence-labelling-part-4-5ei2). **Get the code for this series on [GitHub](https://github.com/fferegrino/vuelax-crf)**.</small>

What good is our system if we can not use it to predict the labels of new sentences. Before that, though, we need to make sure to set up a complete pipeline to go from having a new offer as displayed in the VuelaX site to have a fully labelled offer on our python scripts.

The idea is to borrow functions from all other previous posts; these functions were replicated somewhere inside the `vuelax` packages and are imported to make them less messy to work with.

## We've got a new offer!

Imagine getting a new offer that looks like this:  

 > ¡Sin pasar EE.UU! 🇪🇬¡Todo México a El Cairo, Egipto $13,677!

If your spanish is not on point, I'll translate this for you:

 > Without stops in the USA! 🇪🇬 any airport in México to Cairo, Egypt $13,677!

```python
offer_text = "¡Sin pasar EE.UU! 🇪🇬¡Todo México a El Cairo, Egipto $13,677!"
```

## Steps:

**Tokenise**: the first step was to tokenise it, by using our `index_emoji_tokenize` function

```python
from vuelax.tokenisation import index_emoji_tokenize

tokens, positions = index_emoji_tokenize(offer_text)

print(tokens)
```

**POS Tagging**: the next thing in line is to obtain the POS tags corresponding to each one of the tokens. We can do this by using the `StanfordPOSTagger`:

```python
from nltk.tag.stanford import StanfordPOSTagger

spanish_postagger = StanfordPOSTagger('stanford-models/spanish.tagger', 
                                      'stanford-models/stanford-postagger.jar')

_, pos_tags = zip(*spanish_postagger.tag(tokens))

print(pos_tags)
```

**Prepare for the CRF**: This step involves adding more features and preparing the data to be consumed by the CRF package. All the required methods exist in `vuelax.feature_selection`

```python
from vuelax.feature_selection import featurise_token

features = featurize_sentence(tokens, positions, pos_tags)

print(features[0])
```

**Sequence labelling with pycrfsuite**: And the final step is to load our trained model and tag our sequence:

```python
import pycrfsuite

crf_tagger = pycrfsuite.Tagger()
crf_tagger.open('model/vuelax-bad.crfsuite')

assigned_tags = crf_tagger.tag(features)

for assigned_tag, token in zip(assigned_tags, tokens):
    print(f"{assigned_tag} - {token}")
```  

And the result:

```text
n - ¡
n - Sin
n - pasar
n - EE.UU
n - !
n - ¡
o - Todo
o - México
s - a
d - El
d - Cairo
d - ,
d - Egipto
n - $
p - 13,677
n - !
```

By visual inspection we can confirm that the tags are correct: "Todo México" is the origin (o), "El Cairo, Egipto" is the destination and "13,677" is the price (p).

And that is it. This is the end of this series of posts on how to do sequence labelling with Python. I hope you were able to follow, and if not, I hope you have some questions for me. Remember, post them here or ask me via twitter [@feregri_no](https://twitter.com/feregri_no).

### What else is there to do?  

There are many ways this project could be improved, a few that come to mind:  
    
 - Improve the size/quality of the dataset by labelling more examples
 - Improve the way the labelling happens, using a single spreadsheet does not scale at all
 - Integrate everything under a single processing pipeline
 - "Productionify" the code, go beyond an experiment.
