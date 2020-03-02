---
template: book
original_url: https://dev.to/fferegrino/versioning-any-app-with-python-bij
title: Building Machine Learning Powered Applications
date: 2020-08-06 14:00:00
short_summary: A book about what are the pieces around an application that uses machine learning at its core, a good insight into what is beyond training models.
---  

This is a book about the whole process of putting a machine learning model into production, all the engineering that sometimes the data scientists are not aware of or take for granted. It does not explain any algorithms or how to train a model but what to do before and after we have already trained one. I highly recommend getting this book, specially if you are:   

 - About to start a new machine learning development
 - Coming from the engineering side of software  
 - Want to know what does it take for your new model to become production ready

The book itself is light on code, there is a GitHub repo that the author uses to showcase an entire use case throughout the whole book, however it is possible to just read the book without the need to look at the code, since the code is not the main reason someone would buy this book.

Get the book: <a href="https://www.amazon.com.mx/Building-Machine-Learning-Powered-Applications/dp/149204511X" target="_blank">Amazon Mexico</a>, <a href="https://www.amazon.com/Building-Machine-Learning-Powered-Applications/dp/149204511X" target="_blank">Amazon US</a>

## Some quotes  

> For each successful result published in a research paper or a corporate blog, there are hundreds of reasonable-sounding ideas that have entirely failed.  

> (...) much of the challenge in ML is similar to one of the biggest challenges in software—resisiting the urge to build pieces that are not needed yet.  

> An ML program doesn't just have to run-it should produce accurate predictive outputs.  

> Testing a model's behavior is hard. The majority of code in an ML pipeline is not about the training pipeline or the model itself, however.  

> In reality, most datasets are a collection of approximate measurements that ignore a larger context.  

## Some ideas

 - The idea of using clustering algorithms to guide the exploratory data analysis when it comes to examine individual datapoints, rather than just randomly selecting instances.  
 - What needs to be happen with a model to be deployed on a mobile device.  
 - The idea of having a filtering model, before our actual inference model, that predicts whether the current input will yield an acceptable answer.  
 - The idea of multi-armed bandits to test variants of experiments
 - The idea of federated learning

## Some links

 - <a href="https://blog.insightdatascience.com/automated-front-end-development-using-deep-learning-3169dd086e82" target="_blank">Automated front-end development using deep learning</a>
 - <a href="https://arxiv.org/abs/1705.07962" target="_blank">pix2code: Generating Code from a Graphical User Interface Screenshot</a>
 - <a href="https://arxiv.org/abs/1604.06737" target="_blank">Entity Embeddings of Categorical Variables</a>
 - <a href="https://uchicago-cs.github.io/debugging-guide/" target="_blank">The Debugging Guide by The University of Chicago</a>
 - <a href="https://research.google/pubs/pub46555/" target="_blank">The ML Test Score: A Rubric for ML Production Readiness and Technical Debt Reduction</a>
 - <a href="https://arxiv.org/abs/1810.03993" target="_blank">Model Cards for Model Reporting</a>
 - <a href="http://sites.computer.org/debull/A18dec/p5.pdf" target="_blank">On Challenges in Machine Learning Model Management</a>