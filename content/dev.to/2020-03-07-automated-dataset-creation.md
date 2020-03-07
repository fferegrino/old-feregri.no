---
layout: post
language: en
original_url: https://dev.to/fferegrino/how-to-automate-dataset-creation-with-python-171a
title: Automated dataset creation with Python
date: 2020-03-07 10:00:00
short_summary: I will show you how to generate a dataset from email data, and how to push it to both AWS and Kaggle; all this with Python and some wonderful packages.
tags: kaggle, python, medium
---

## Background (or why did I do this)

I have been trying to create a dataset related to Medium posts, despite there [being](https://www.kaggle.com/harrisonjansma/medium-stories) some [already](https://www.kaggle.com/hsankesara/medium-articles/kernels) out there. However, it seems that they are focused on certain topics, or just too small; I wanted my dataset to be something different but still related to Medium.

As for the data, I am certainly not sure about whether the dataset will be helpful to anyone, but I hope the way I built it with Python will be useful for anyone with more critical data out there.

PS: Look what the result of what I am explaining here is: [Medium Daily Digests on Kaggle](https://www.kaggle.com/ioexception/medium-daily-digests).

## Data source and collection  

So if I wanted my dataset to be unique and different, I had to do something extra. At first, I thought of massively scraping posts from Medium; the problem is that they do not provide an easy to crawl, easy to scrape website… then I thought about that *"Medium Daily Digest"* that I get every day, in it, Medium sends me stories that "I may be interested in"; Going back to when I subscribed to it I remember having to choose my interests among several topics.  

With that in mind I set out to create 20 different email accounts (in reality they are aliases to a single account) and then use each one of them to subscribe to this infamous *"Medium Daily Digest"*, each account associated with five different (but somehow related as judged by me) topics. And ever since then I have been receiving 20 emails, every single day with titles, subtitles images and juicy urls. 

Every now and then I log in to those accounts, open a few emails to prevent said accounts to be trimmed from Medium's syndication because [they know when you are not opening their emails](https://www.theverge.com/2019/7/3/20681508/tracking-pixel-email-spying-superhuman-web-beacon-open-tracking-read-receipts-location) but nothing major. It is also expected that the topics they offer may change over time, and at some point the interest of some accounts may chang,  then I'll have to log into Medium and do it myself manually, but for the most part the data collection runs on its own.

## Pulling emails from the server  

As mentioned above, the emails are delivered to my email account, and there is no fun in having to download 20 emails manually every single day, so, for the first time in this article: Python to the rescue.

To access the emails on my server, I use the IMAP protocol; this allows me to read them and keep them there, just in case I want to access them in the future. For this, even though Python offers a built-in module called `imaplib` to interact with such servers, I decided to use the package `imapclient` wich, in my opinion, makes the code a bit cleaner and understandable. To read all the emails in an account is just as easy as this snippet of code shows:

```python
import email
from imapclient import IMAPClient

with IMAPClient(host=imap_server, use_uid=True) as client:  
    client.login(account, password)  
    messages = client.search(["NOT", "DELETED"])  
    for message_id in messages:  
        fetched = client.fetch(message_id, "RFC822")  
        data = fetched[message_id]  
        email_message = email.message_from_bytes(data[b"RFC822"])
        yield message_id, email_message
```

As you can see, we use `IMAPClient`as a context manager, then we login using our email credentials (yes, it is a shame we have to use our password directly); after logging in we search all the `NOT` `DELETED` emails, this will return a list of strings containing the identifiers for each message; we can iterate over these ids and use the client to `fetch` each message specifying that we want the `RFC822` property of the email. The return value of this call will be a dictionary of the shape `{ message_id: { b"RFC822": (bytes) } }`, we can easily transform these bytes to a more pythonic email representation by using the `message_from_bytes` function. You can see my actual implementation by looking at the function [`read_from_mail`](https://github.com/fferegrino/medium-collector/blob/v0.0.0/medium_collector/download/reader.py#L6) in my repo.

## Extracting email data  

Once I have an email that is easy to work with in Python, I will refer to my previous post on [how to read emails with Python](https://dev.to/fferegrino/reading-emails-with-python-4o72). Once we can interpret the message we can access properties such as `To`, `From`,  `Subject` and `Date`, as well as access the actual content of the email. For reference look at this snippet of code where `message` is what we get from calling `message_from_bytes` in the previous snippet:

```python
import datetime
import quopri

parts = {part.get_content_type(): part for part in message.get_payload()}  
html = quopri.decodestring(parts["text/html"].get_payload()).decode("utf8")   
mail_info = {  
    "id": message["Message-ID"],  
    "to": message["To"],  
    "from": message["From"],  
    "date": datetime.datetime.strptime(  
        message.get("Date"), "%a, %d %b %Y %H:%M:%S +0000 (%Z)"  
    ),  
}
```
The end result of this snippet is to produce a dictionary (`mail_info`) containing basic email information, and the html version of the email `html`. You can see my actual implementation in the function [`parse_mail`](https://github.com/fferegrino/medium-collector/blob/v0.0.0/medium_collector/download/parser.py#L34).

To work with the HTML of the email I used BeautifulSoup, I will not go into details, but as always with web scraping, it was a process of trial and error to get the appropriate structure to extract information from the content of the email. You can see the full parsing function [here](https://github.com/fferegrino/medium-collector/blob/master/medium_collector/download/parser.py#L50), it all boils down to end with a list of dictionaries (one for each post in the email) with the following information: *section_title*, *post_title*, *post_subtitle*, *post_url*, *author_name*, *author_handle*, *site_name*, *site_slug*, *members_only*:

![Extraction description](https://i.imgur.com/jmkVSgz.png)  
<small>(in hindsight I could have extracted the read time, maybe in the next version)</small>.

## Saving the data  

After downloading the information, it is saved to two csv files: 
 - *mails.csv*, which is an archive of all the emails received, this contains:
	 - **id**: a unique identifier of the email
	 - **date**: the datetime when the email was received
	 - **to**: a hash of the email account this email was delivered to
	 - **from**: the email account used to send the email (it is always the same)
	 - **subject**: the subject of the email
 - *articles_mails.csv*, contains the information extracted from each email, associated to the email they came from:  
	 - **mail_id**: a unique identifier of the email this article came from, corresponds to one of **id** in the *mails.csv* file
	 - **post_url**: the medium url of the article
	 - **post_title**: the title of the article
	 - **post_subtitle**: the subtitle of the article 
	 - **section_title**: the title of the section the post was listed under
	 - **members_only**: a boolean flag that specifies whether the article is for members of Medium
	 - **author_name**: name of the article's author
	 - **author_handle**: handle of the article's author
	 - **site_name**: if the article was published under a site, this contains the name of such site
	 - **site_slug**: if the article was published under a site, this contains the handle of such site  
	 
To write all this information to the files I used the always reliable `csv` module, in particular, the `DictWriter` class that allows the usage of dictionaries when calling the `writerow` method:

```python
import csv

EMAILS_FILE_HEADERS = ["id", "date", "to", "from", "subject"]
emails = [{"id": 1, "date": datetime.now(), 
           "to": "cosme@fulanito.com", "from": "noreply@medium.com",
	   "subject": "Don't miss this!"}]

with open("mails.csv", "w") as writable:
	writer = csv.DictWriter(writable, fieldnames=EMAILS_FILE_HEADERS)
	writer.writeheader()
	for email in emails:
		writer.writerow(email)
```  

In reality what I do is slightly more complicated since I want to add rows to the dataset incrementally; so instead the file must be opened with `"a"` as file mode, not `"w"` and special care is needed to not write the headers in the middle of the file either. You can check the whole implementation of the writing functions [in this piece of code](https://github.com/fferegrino/medium-collector/blob/v0.0.0/medium_collector/download/writer.py).

## Pushing data to S3  

But what good is this data if it is going to live sitting there on my computer? To overcome this issue, I thought of uploading the data to an S3 bucket, so as to make it available for me to download it anywhere I need it. To access any AWS resource my favourite tool is the package `boto3` which in is a true swiss knife for AWS. 

Supposing that you want to upload the file `medium_data/mails.csv` to the bucket `"medium_bucket"` and have it named `"mails.csv"` in there, the following code will suffice:  

```python
import boto3

bucket = "my_super_cool_bucket"
client = boto3.client(  
	"s3",
	aws_access_key_id=config("ACCESS_KEY"),
	aws_secret_access_key=config("SECRET_KEY"),  
	region_name="eu-west-2",  
)

client.upload_file("medium_data/mails.csv", bucket, "mails.csv")
```

But I do not want to keep uploading the same file over and over if there is no need to do so. To accomplish this, it is possible to check if the file exists in our bucket and have its content summarised with an `md5` hash generated by AWS itself. Then it is just a matter of comparing said hash with the hash of the local file and if they are the same, I do not upload the file:

```python
import hashlib

def get_file_hash(file_path):   
	hash_md5 = hashlib.md5()  
	with open(file_path, "rb") as readable:  
		for chunk in iter(lambda: readable.read(4096), b""):  
			hash_md5.update(chunk)  
	return hash_md5.hexdigest()

head = client.head_object(Bucket=bucket, Key="mails.csv")
md5_signature = get_file_hash("medium_data/mails.csv")
if "ETag" in head and literal_eval(head["ETag"]) == md5_signature:
	# The file already exists, do nothing
else:
	client.upload_file("medium_data/mails.csv", bucket, "mails.csv")
```

The method that one needs to call to get information for an object is `head_object`. By the way, the whole logic and implementation is in [this file](https://github.com/fferegrino/medium-collector/blob/v0.0.0/medium_collector/s3.py) if you want to check it out.

*Some considerations*: For this example, I considered that the bucket already exists, however, if it does not, it is also possible to use *boto* to create it.  As I said, *boto* is an absolute monster of a library that you should consider if working with AWS. I am also using the credentials directly on the call to the s3 client creation, but there are multiple ways to handle authentication with *boto*, check the documentation to learn more.


## Pushing data to Kaggle  

So far, everything is going great, but the dataset is still available to me, and while I could make my s3 bucket public, there are a few issues with this approach:  
 - I do not want my S3 bill to go up the sky if someone with malicious intent gets a hold of my s3
 - I want people to use the data, and a random s3 url is not very easy to discover or promote

But there is a good place to store datasets, it is free and, at the same time, it indexes the data and makes it discoverable to the public in generar. I am talking about Kaggle.

Kaggle makes it relatively easy to interact with some of the resources the website offer via their [kaggle-api](https://github.com/Kaggle/kaggle-api) package. In general, they promote the interaction vía the command line, however, it is also possible to use the programmatic API that power the *cli*. To upload a new version of my dataset I had to do something like this:

```python
from kaggle import api

def upload_to_kaggle(data_folder, message):
	api.dataset_create_version(data_folder, message, quiet=True)
	
upload_to_kaggle("medium_data", "A new version of this dataset")
```

And that is it. Really, it is that easy. But not so fast, that is if we want to update a dataset, if we are creating one from scratch we first need to perform three things:  
 - Create a folder (say, `"medium_data"`) where only the files corresponding to our dataset exist
 - Have a `dataset-metadata.json` file in that folder with the metadata for your dataset, the file looks should look like the one below (but you can [check mine](https://github.com/fferegrino/medium-collector/blob/v0.0.0/data/dataset-metadata.json) if you need a more concrete example):
```
{
  "title": "My Awesome Dataset", 
  "id": "cosme_fulanito/my-awesome-dataset", 
  "licenses": [{"name": "CC0-1.0"}]
}
```
 - Call either `kaggle datasets create -p medium_data` on the console, or use the `dataset_create_new` programmatically.

I did perform those tasks manually since it is not like I will be creating datasets programmatically but just updating them, your use case may be different. 

*Some considerations*: Just like AWS, Kaggle also offers some ways of authenticating with their service, I used the one they promote the most: a `kaggle.json` file in `~/.kaggle`, but you may use something different.

## Testing  

As with any piece of software that is to be released and meant to run unattended (not to mention that my s3 bill depends on this thing working properly), it is good to have some testing just to make sure it will do what I programmed it to do. However, I initially intended to write about testing in this post, but it is already long as it is currently, so I will be publishing how I tested the app in a future post, so make sure you are following me if you want to learn about testing, patching and mocking (including mocking aws).

### Any question or comments?  

Feel free to leave a comment below, or tweet at me at [@io_exception](https://twitter.com/io_exception), I am more than happy to help you if things are not clear and need further explanation about some piece of code. Remember that the whole app is [available on GitHub](https://github.com/fferegrino/medium-collector/tree/v0.0.0) for you to tinker around with it.


