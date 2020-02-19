---
layout: post
language: en
original_url: https://dev.to/fferegrino/sequence-labelling-in-python-part-1-4noa
title: Sequence labelling in Python (part 1)
date: 2020-01-14 10:00:00
tags: python, data-science, nlp
short_summary: Or how to find the best flight deals for the holidays with programming.
---

## Why?

I was looking for a cool project to practice sequence labelling with Python so... there is this Mexican website called [VuelaX](https://www.vuelax.com), in it, flight offers are shown. Most of the offers follow a simple pattern: *Destination - Origin - Price - Extras*, while extracting this may seem easy for a regular expression, it is not as there are many patterns. It would be tough for us to cover them all.

 > I know it is not ideal to work in a foreign language, but bear with me, as the same techniques could be applied in your language of choice.

The idea is to create a tagger that will be able to extract this information. However, one first tag is to identify the information that we want to extract. Following the pattern described above:

 - **o**: Origin
 - **d**: Destination
 - **s**: Separator token
 - **p**: Price
 - **f**: Flag
 - **n**: Irrelevant token

| Text     | d    | o    | p    | n    |
|------    |----- |----- |----- |----- |
| ¡CUN a Holanda $8,885! Sin escala EE.UU | CUN | Holanda | 8,885 | Sin escala EE.UU |
| ¡CDMX a Noruega $10,061! (Y agrega 9 noches de hotel por $7,890!) | CDMX | Noruega | 10,061 | Y agrega 9 noches de hotel por $7,890!|
| ¡Todo México a Pisa, Toscana Italia $12,915! Sin escala EE.UU (Y por $3,975 agrega 13 noches hotel) | México | Pisa, Toscana Italia | 12,915 | Sin escala EE.UU (Y por $3,975 agrega 13 noches hotel) |

## CRFs in Python

If you are familiar with data science, you know this is known as a sequence labelling problem. While there are various ways to approach it, in this post, I will show you one that uses a statistical model known as Conditional Random Fields. Having said that, I will not delve too much into details, so if you want to learn more about CRFs you are on your own; I will show you a practical way to use it with a Python implementation.

## Getting some data  

To start, I scraped the offer titles data from the page mentioned above. I will not detail how I did it since it is pretty straightforward to find a tutorial on [web scraping on the web](https://realpython.com/beautiful-soup-web-scraper-python/). If you don't feel like spending some time scraping a website, I collected some data in a CSV file that you can [access now here](https://github.com/fferegrino/vuelax-crf/blob/master/data/vuelos.csv).

This tutorial will be divided into other 4 parts:  

 - [Part-Of-Speech tagging (and getting some ground truth)](https://dev.to/fferegrino/part-of-speech-tagging-sequence-labelling-in-python-part-2-4o66)
 - [Other feature extraction](https://dev.to/fferegrino/extracting-more-features-sequence-labelling-in-python-part-3-3389)
 - [Conditional Random Fields with python-crfsuite](https://dev.to/fferegrino/conditional-random-fields-in-python-sequence-labelling-part-4-5ei2)
 - [Putting everything together](https://dev.to/fferegrino/putting-everything-together-sequence-labelling-in-python-part-5-19ng)

Hopefully, you will follow along and will ask some questions if you have by leaving a comment here or contacting me on twitter via [@io_exception](https://twitter.com/io_exception).
