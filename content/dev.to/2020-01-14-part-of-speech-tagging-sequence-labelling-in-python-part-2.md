---
layout: post
language: en
original_url: https://dev.to/fferegrino/part-of-speech-tagging-sequence-labelling-in-python-part-2-4o66
title: Part of speech tagging - Sequence labelling in Python (part 2) 
date: 2020-01-14 11:00:00
tags: python, data-science, nlp
short_summary: How to get part of the speech tags with Python using NLTK
---  

<small>This is the second post in my series *Sequence labelling in Python*, find the previous one here: [Introduction](https://dev.to/fferegrino/sequence-labelling-in-python-part-1-4noa). **Get the code for this series on [GitHub](https://github.com/fferegrino/vuelax-crf)**.</small>

Our algorithm needs more than the tokens themselves to be more reliable; We can add [part of speech](https://en.wikipedia.org/wiki/Part_of_speech) as a feature. 

To perform the Part-Of-Speech tagging, we'll be using the [Stanford POS Tagger](https://nlp.stanford.edu/software/tagger.shtml); this tagger (or at least the interface to it) is available to use through Python's NLTK library; however, we need to download some models from the [Stanford's download page](https://nlp.stanford.edu/software/tagger.shtml#Download). In our case, since we are working with spanish, we should download the *full* model under the *"2017-06-09 new Spanish and French UD models"* subtitle.

Once downloaded, it is necessary to unzip it and keep track of where the files end up being. You could execute:

```shell
make models/stanford
```

To get the necessary files inside a folder called `stanford-models`. **Be aware that you will need to have Java installed for the tagger to work!**

## Code  

Let us start with some imports and loading our dataset:  

```python
import json
import pandas as pd

# Load dataset:
vuelos = pd.read_csv('data/vuelos.csv', index_col=0)
with pd.option_context('max_colwidth', 800):
    print(vuelos.loc[:40:5][['label']])
``` 

Some of the results:  


```
0                                           ¡CUN a Ámsterdam $8,960! Sin escala en EE.UU
5              ¡GDL a Los Ángeles $3,055! Directos (Agrega 3 noches de hotel por $3,350)
10                      ¡CUN a Puerto Rico $3,296! (Agrega 3 noches de hotel por $2,778)
15    ¡LA a Seúl, regresa desde Tokio 🇯🇵 $8,607! (Por $3,147 agrega 11 noches de hostal)
20                           ¡CDMX a Chile $8,938! (Agrega 9 noches de hotel por $5,933)
25                                               ¡CUN a Holanda $8,885! Sin escala EE.UU
30                              ¡Todo México a París, regresa desde Amsterdam – $11,770!
35  ¡CDMX a Vietnam $10,244! Sin escala en EE.UU (Agrega 15 noches de hostal por $2,082)
40                     ¡CDMX a Europa en Semana Santa $14,984! (París + Ibiza + Venecia)
```  

To interface with the Stanford tagger, we could use the `StanforPOSTagger` inside the `nltk.tag.stanford` module, then we create an object passing in both our language-specific model as well as the tagger `.jar` we previously downloaded from Stanford's website.  

Then, as a quick test, we tag a spanish sentence to see what is it that we get back from the tagger.

```python  
from nltk.tag.stanford import StanfordPOSTagger

spanish_postagger = StanfordPOSTagger('stanford-models/spanish.tagger', 
                                      'stanford-models/stanford-postagger.jar')

phrase = 'Amo el canto del cenzontle, pájaro de cuatrocientas voces.'
tags = spanish_postagger.tag(phrase.split()) 
print(tags)
```

The results:  

```text  
[('Amo', 'vmip000'), ('el', 'da0000'), ('canto', 'nc0s000'), 
('del', 'sp000'), ('cenzontle,', 'dn0000'), ('pájaro', 'nc0s000'), 
('de', 'sp000'), ('cuatrocientas', 'pt000000'), ('voces.', 'np00000')]
```

The first thing to note is the fact that the tagger takes in lists of strings, not a full sentence, that is why we need to split our sentence before passing it in. A second thing to note is that we get back of tuples; where the first element of each tuple is the token and the second is the POS tag assigned to said token. The POS tags are [explained here](https://nlp.stanford.edu/software/spanish-faq.html), and I have made a dictionary for easy lookups.

We can inspect the tokens a bit more:

```python
with open("aux/spanish-tags.json", "r") as r:
    spanish_tags = json.load(r)
    
for token, tag in tags[:10]:
    print(f"{token:15} -> {spanish_tags[tag]['description']}")
```

And the results:  

```text
Amo             -> Verb (main, indicative, present)
el              -> Article (definite)
canto           -> Common noun (singular)
del             -> Preposition
cenzontle,      -> Numeral
pájaro          -> Common noun (singular)
de              -> Preposition
cuatrocientas   -> Interrogative pronoun
voces.          -> Proper noun
```

## Specific tokenisation  

As you may imagine, using `split` to tokenise our text is not the best idea; it is almost certainly better to create our function, taking into consideration the kind of text that we are going to process. The function above uses the `TweetTokenizer` and considers flag emojis. As a final touch, it also returns the position of each one of the returned tokens:

```python
from nltk.tokenize import TweetTokenizer

TWEET_TOKENIZER = TweetTokenizer()

# This function exists in vuelax.tokenisation in this same repository
def index_emoji_tokenize(string, return_flags=False):
    flag = ''
    ix = 0
    tokens, positions = [], []
    for t in TWEET_TOKENIZER.tokenize(string):
        ix = string.find(t, ix)
        if len(t) == 1 and ord(t) >= 127462:  # this is the code for 🇦
            if not return_flags: continue
            if flag:
                tokens.append(flag + t)
                positions.append(ix - 1)
                flag = ''
            else:
                flag = t
        else:
            tokens.append(t)
            positions.append(ix)
        ix = +1
    return tokens, positions


        

label = vuelos.iloc[75]['label']
print(label)
print()
tokens, positions = index_emoji_tokenize(label, return_flags=True)
print(tokens)
print(positions)
```

And these are the results:

```text
¡LA a Bangkok 🇹🇭$8,442! (Por $2,170 agrega 6 noches de Hotel)

['¡', 'LA', 'a', 'Bangkok', '🇹🇭', '$', '8,442', '!', '(', 'Por', '$', '2,170', 'agrega', '6', 'noches', 'de', 'Hotel', ')']
[0, 1, 4, 6, 14, 16, 17, 22, 24, 25, 16, 30, 36, 43, 45, 52, 55, 60]
```

## Obtaining our ground truth for our problem 


**We do not need POS Tagging to generate a tagged dataset!**. 

Now, since this is a supervised algorithm, we need to get some labels from *"expert"* users. These labels will be used to train the algorithm to produce predictions. The task for the users will be simple: assign one of the following letters to each token: `{ o, d, s, p, f, n }`. While there are [online tools](https://doccano.herokuapp.com/) to perform this task, I decided to go more old school with a simple CSV file with a format more or less like this:

| Offer Id | Token | Position | POS | Label |  
|--------  |-----  |--------- |---- |------ |
| 0 | ¡ | 0 | faa | [USER LABEL] |  
| 0 | CUN | 1 | np00000 | [USER LABEL] |  
| 0 | a | 5 | sp000 | [USER LABEL] |  
| 0 | Ámsterdam | 7 | np00000 | [USER LABEL] |  
| 0 | $ | 17 | zm | [USER LABEL] |  
| 0 | 8,960 | 18 | dn0000 | [USER LABEL] |  
| 0 | ! | 23 | fat | [USER LABEL] |  
| 0 | Sin | 25 | sp000 | [USER LABEL] |  
| 0 | escala | 29 | nc0s000 | [USER LABEL] |  
| 0 | en | 36 | sp000 | [USER LABEL] |  
| 0 | EE.UU | 39 | np00000 | [USER LABEL] |   

Where the values of the column marked with `[USER LABEL]` should be defined by the expert users who will help us in labelling our data.

```python
from tqdm.notebook import trange, tqdm
import csv

path_for_data_to_label = "data/to_label.csv"

with open(path_for_data_to_label, "w") as w:
    writer = csv.writer(w)
    writer.writerow(['offer_id', 'token', 'position', 'pos_tag', 'label'])
    
    for offer_id, row in tqdm(vuelos.iterrows(), total=len(vuelos)):
        tokens, positions = index_emoji_tokenize(row["label"], return_flags=True)
        tags = spanish_postagger.tag(tokens)
        for  token, position, (_, pos_tag) in zip(tokens, positions, tags):
            writer.writerow([
                offer_id,
                token,
                position,
                pos_tag,
                None
            ])
        
```

The file that needs to be labelled is located at `data/to_label.csv`.

**Can we make this easy?** I have gone through the *"pains"* of labelling some data myself; the labels are stored in the file `data/to_label-done.csv`.

Visit the next post in the series: [Other feature extraction](https://dev.to/fferegrino/extracting-more-features-sequence-labelling-in-python-part-3-3389). In the meantime, I hope this post has shed some light on how to use the `StanfordPOSTagger`; feel free to ask some questions if you have them by leaving a comment here or contacting me on twitter via [@io_exception](https://twitter.com/io_exception).