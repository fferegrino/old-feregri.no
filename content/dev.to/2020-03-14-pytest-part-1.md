
---
title: Unit testing with pytest
published: false
description: I will show you how to generate a dataset from email data, and how to push it to both AWS and Kaggle; all this with Python and some wonderful packages.
tags: pytest, moto, aws, python
---

#### Disclaimer

Throughout this post I will be testing functions from the code I wrote to [scrape emails and upload the information to Kaggle](https://dev.to/fferegrino/how-to-automate-dataset-creation-with-python-171a) however, it is not necessary that you read that post first, but it will give more context to the code being tested here.

## What is pytest?  
Pytest is a testing framework for Python that supports automatic collection of tests; simple asserts; support for test fixtures and state management, debugging capabilities and many things more. via customized traceback. Do not worry if some of those terms make little sense to you, I will try to clarify them as we go along the post.

By the way, pytest is not the only testing framework available: nose, doctest, testify... but pytest is the one I use and the one I know most about.

## Writing our tests

## Parametrising our tests 
Let's start by writing a simple test: single input, single output, no calls to any external service. I am talking about a function that takes an encoded string and returns a human readable sentence, I am talkig about the :

## Patching

### Dangers of overpatching

## Fixtures

### Why do we need fixtures?

## Advanced fixtures


## Going beyond unit tests


