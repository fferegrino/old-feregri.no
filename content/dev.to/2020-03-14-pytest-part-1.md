---
title: Unit testing with pytest
published: false
description: I will show you how to generate a dataset from email data, and how to push it to both AWS and Kaggle; all this with Python and some wonderful packages.
tags: pytest, moto, aws, python
---

#### Disclaimer

Throughout this post I will be testing functions from the code I wrote to [scrape emails and upload the information to Kaggle](https://dev.to/fferegrino/how-to-automate-dataset-creation-with-python-171a) however, it is not necessary that you read that post first, but it will give more context to the code being tested here.

## What is *pytest*?  
*pytest* is a testing framework for Python that supports automatic collection of tests, simple asserts, support for test fixtures and state management, debugging capabilities and many things more. Do not worry if some of those terms make little sense to you, I will try to clarify them as we go along the post.

By the way, *pytest* is not the only testing framework available: nose, doctest, testify... but *pytest* is the one I use and the one I know most about.

## Writing our tests

## Parametrising our tests 
Let's start by writing a simple test: single input, single output, no calls to any external service. I am talking about a function that takes an encoded string (like `=?UTF-8?B?VGhlcmXigJlz?= more to the story`) and returns a human readable sentence (like `There’s more to the story`), I am talking about the [`get_subject` method](https://github.com/fferegrino/medium-collector/blob/v0.0.0/medium_collector/download/parser.py#L12):

```python
def get_subject(subject):
    subject_parts = []
    subjects = email.header.decode_header(subject)
    for content, encoding in subjects:
        try:
            subject_parts.append(content.decode(encoding or "utf8"))
        except:
            subject_parts.append(content)
    return "".join(subject_parts)
```

So to write a test using pytest is just as easy as:

```python
def test_get_subject():
    expected = "There’s more to the story"
    actual = get_subject("=?UTF-8?B?VGhlcmXigJlz?= more to the story")
    assert expected == actual
```
However, the function needs to be tested against the case where all the string is encoded, and the case where none of it is encoded. To cover these cases we could write `test_get_subject_all_encoded` and `test_get_subject_none_encoded` but that would be just useless code duplication, to tackle this problem of **testing same code with multiple inputs** we could use test parametrisation via the `@pytest.mark.parametrize` decorator:

```python
import pytest

@pytest.mark.parametrize(
    ["input_subject", "expected"],
    [
	# Input 1
        (
            "=?UTF-8?B?V2hlbiBhICQxMDAsMDAwIFNhbGFyeSBJc27igJl0IEVub3VnaCB8IEFkYW0gUGFyc29ucyBpbiBNYWtpbmcgb2YgYSBNaWxsaW8=?= =?UTF-8?B?bmFpcmU=?=",
            "When a $100,000 Salary Isn’t Enough | Adam Parsons in Making of a Millionaire",
        ),
	# Input 2
        (
            "=?UTF-8?B?VGhlcmXigJlz?= more to the story", 
            "There’s more to the story"
	),
	# Input 3
        (
            "7 Things Rich People Advise But Never Do | David O. in The Startup",
            "7 Things Rich People Advise But Never Do | David O. in The Startup",
        ),
    ],
)
def test_get_subject(input_subject, expected):
    actual = get_subject(input_subject)
    assert actual == expected
```

The above code will effectively instruct *pytest* execute the test `test_get_subject` three times, each time replacing `input_subject`, `expected` for the corresponding values specified in the second argument of `parametrize`. 

## Fixtures
Some of the time we may have **tests that need to start from a certain state**, this state may mean having data in a database, having some files on a certain location, or maybe just having the right object as input to the function. That is when fixtures come in handy.  

For example, in the *medium-collector* app I mentioned at the top of the post, there is a method called `parse_mail` that, as the name suggests, we can use to extract information from an object of the class `email.message.Message`.  Have a quick glance at a simplified version of the method's implementation:

```python
def parse_mail(email_message):
    html = get_html(email_message)
    mail_info = {
        "id": email_message["Message-ID"],
        "to": email_message["To"],
        "from": email_message["From"],
        "subject": get_subject(email_message["Subject"]),
        "date": email_message["Date"],
    }
    return mail_info, html
``` 
To test this method we need an object of the class `Message`, but we don't really want to keep contacting our email server each time we run the test; this makes up for the perfect scenario for a fixture. To define one in *pytest* we need to write it as follows:

```python
@pytest.fixture
def dummy_mail():
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Link"
    msg["From"] = "you@this.com"
    msg["To"] = "me@that.com"
    msg["Message-ID"] = "123"
    msg["Date"] = datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000 (UTC)")
    
    text = "Hi!"
    html = f"<html><head></head><body><p>{text}<br></body></html>"
    msg.attach(MIMEText(text, "plain"))
    msg.attach(MIMEText(html, "html"))

    return msg
 ``` 

The first thing to note is the `@pytest.fixture`  as a decorator of a... function!? Yes, that is it, a fixture is nothing but a function whose return value must be the value we want that fixture to have. In this case the value of the fixture will be an object of the class `MIMEMultipart` which inherits from `Message`, just what we wanted. 

Now, to use our fixture named `dummy_mail` in our test it is enough to pass it as an argument of our test method:

```python
def test_parse_mail(dummy_mail):
    expected_mail_info = {
        "id": "ad841b37bd4b9b5403b575432f67f5ed2d68ed40",
        "to": "a4747a50dad63531704f5ab32509bb0c60b7350f",
        "from": "you@this.com",
        "subject": "Link",
        "date": ANY,
    }
    mail_info, decoded = parse_mail(dummy_mail)

    assert mail_info == expected_mail_info
    assert decoded == "<html><head></head><body><p>Hi!<br></body></html>"
```

The way *pytest* works is by resolving the fixtures first, before any test that uses them is run, and once they are ready, the test method gets executed receiving the values of the fixtures it uses. This mechanism allows some very interesting uses that I will cover in a few sections below.

### An extra feature with fixtures  
*pytest* fixtures are just great, another use is when we want to reuse the same piece of code in two or more test methods, imagine we needed to use a `Message` for two test methods. We could have simply declared a global variable, say `MESSAGE = MIMEMultipart("alternative")`  and then use it in our methods like: 

```python
def test_parse_mail_1():
	parse_mail(MESSAGE)
	# ...
	
def test_parse_mail_2():
	parse_mail(MESSAGE)
	# ...
```

But in this case both our tests would be using the same variable `MESSAGE`, that means that any change made by `test_parse_mail_1` would affect the `MESSAGE` that `test_parse_mail_2` receives, this breaks the purpose of unit testing as our tests would not be isolated any more.  However, when we use fixtures, each test method will receive a *fresh* copy of the return value specified by the fixture body, making it easy to reuse them over and over again.

## Patching
Without a doubt some parts of our code will rely on third party libraries or external services that we do not want to execute or contact while running our tests; whether it be because the library you are calling consumes a lot of resources or it is a production system that should not be touched while testing. Here is when patching come in handy; it helps us in replacing the functionality of a function call with whatever we want to.

Imagine that the function `get_html` code is a very *"expensive"* one, and we don't want to execute every time we execute the `test_parse_mail` we could just patch it (I must say, patching is not a feature of *pytest* itself, it comes with python inside the module `unittest.mock`).

There are two ways to patch, the first one is using the `with` statement, passing in the fully qualified name of the function we want to patch to the `patch` call; a test that patches `get_html` inside `parse_email` would look like this:

```python
from unittest.mock import patch

def test_parse_mail(dummy_mail):
    expected_mail_info = {
        "id": "ad841b37bd4b9b5403b575432f67f5ed2d68ed40",
        # ...
    }
    
    with patch("medium_collector.download.parser.get_html", 
		return_value="Hello") as patched:
	    mail_info, decoded = parse_mail(dummy_mail)

    patched.assert_called_once()
    assert mail_info == expected_mail_info
    assert decoded == "Hello"
```  
In the previous snippet, we are patching the function and assigning it `"Hello"` as its `return_value`, that is a value that must be returned every that function is called. Now that our function is not called, we can make sure we did call it by asserting it was, each `patch` instance  offers a set of methods that make it easy for us to find out whether they were called, how many times they were called, as well as the arguments used to invoke them; for now we just check it was called with `assert_called_once`.

### Perils of patching
Patching may look like an easy solution to avoid contacting external services or expensive function calls, however, you must know that you are making some big assumptions about the code being patched:  
 - You know the expected behaviour of the code being patched (you know what it returns and how it fails). 
 - You are able to realistically mock any return value of the code being patched. 

When patching just be aware that what you are patching may return a complex type that is really hard to mimic, and patching it badly may result on testing against a scenario your code will not find 


## Advanced fixtures


## Going beyond unit tests
