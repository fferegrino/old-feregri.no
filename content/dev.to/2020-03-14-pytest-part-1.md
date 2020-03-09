---
title: Unit testing with pytest
published: false
description: I will show you how to generate a dataset from email data, and how to push it to both AWS and Kaggle; all this with Python and some wonderful packages.
tags: pytest, moto, aws, Python
---

#### Disclaimer

Throughout this post, I will be testing functions from the code I wrote to [scrape emails and upload the information to Kaggle](https://dev.to/fferegrino/how-to-automate-dataset-creation-with-python-171a) however, it is not necessary that you read that post first, but it will give more context to the code being tested here.

## What is *pytest*?  
*pytest* is a testing framework for Python that supports automatic collection of tests, simple asserts, support for test fixtures and state management, debugging capabilities and many things more. Do not worry if some of those terms make little sense to you; I will try to clarify them as we go along the post.

By the way, *pytest* is not the only testing framework available: nose, doctest, testify... but *pytest* is the one I use and the one I know most about.

To get *pytest* you can download it from PyPI with your package manager of choice:

```shell
pip install pytest
```

## Writing our tests  

To create test functions that *pytest* recognises automatically it is necessary to create them with `test_` as a name prefix. We need to name them like that since when we execute *pytest* we must specify a root directory, from this directory, *pytest* will read all our files (within this directory), in search of the `test_`-prefixed functions. For example, if you have a look at the [*medium-collector* repo](https://github.com/fferegrino/medium-collector), you will see that all the tests are contained within the appropriately named `tests` folder. To execute them all we need to do is to call *pytest* with the folder name as an argument, and it will automatically traverse this directory searching for our tests:

```shell
pytest tests/
```

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

So to write a test using *pytest* is just as easy as:

```python
def test_get_subject():
    expected = "There's more to the story"
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

For example, in the *medium-collector* app I mentioned at the top of the post, there is a method called `parse_mail` that, as the name suggests, we can use to extract information from an object of the class `email.message.Message`.  Have a glance at a simplified version of the method's implementation:

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

The first thing to note is the `@pytest.fixture`  as a decorator of a... function!? Yes, that is it, a fixture is nothing but a function whose return value must be the value we want that fixture to have. In this case, the value of the fixture will be an object of the class `MIMEMultipart` which inherits from `Message`, just what we wanted. 

Now, to use our fixture named `dummy_mail` in our test, it is enough to pass it as an argument of our test method:

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

The way *pytest* works is by resolving the fixtures first before any test that uses them is run, and once they are ready, the test method gets executed receiving the values of the fixtures it uses. This mechanism allows some very interesting uses that I will cover in a few sections below.

### An extra feature with fixtures  
*pytest* fixtures are just great, and another use is when we want to reuse the same piece of code in two or more test methods, imagine we needed to use a `Message` for two test methods. We could have declared a global variable, say `MESSAGE = MIMEMultipart("alternative")`  and then use it in our methods like: 

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
Without a doubt, some parts of our code will rely on third-party libraries or external services that we do not want to execute or contact while running our tests. Whether it be because the library you are calling consumes a lot of resources or it is a production system that should not be touched while testing. Here is when patching comes in handy; it helps us in replacing the functionality of a function call with whatever we want to.

Imagine that the function `get_html` code is a very *"expensive"* one, and we don't want to execute every time we run the `test_parse_mail` we could patch it (I must say, patching is not a feature of *pytest* itself, it comes with Python inside the module `unittest.mock`).

There are two ways to patch; one is using the `with` statement, passing in the fully qualified name of the function we want to patch to the `patch` call; a test that patches `get_html` inside `parse_email` would look like this:

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

In the previous snippet, we are patching the function and assigning it `"Hello"` as its `return_value`, that is a value that must be returned every that function is called. Now that our function is not called, we can make sure we did call it by asserting it was, each `patch` instance offers a set of methods that make it easy for us to find out whether they were called, how many times they were called, as well as the arguments used to invoke them; for now we check it was called with `assert_called_once`.

### Perils of patching
Patching may look like an easy solution to avoid contacting external services or expensive function calls. However, you must know that you are making some significant assumptions about the code being patched:  
 - You know the expected behaviour of the code being patched (you know what it returns and how it fails). 
 - You can realistically mock any return value of the code being patched. 

When patching be aware that what you are patching may return a complex type that is hard to mimic, and patching it badly may result on you testing against a scenario your code will not find in real life. To overcome this, you may have to examine with detail what are the return values of what you are patching to do it correctly.

Another common problem with patching is that at some point we may get carried over and just end up patching everything... which again, makes up for tests that are not really testing scenarios that your code will not find. If you find yourself doing this, it is probably worth reconsidering if unit testing is the right approach for that specific piece of code, maybe an integration test is better in that case.

## *"Advanced"* fixtures
As mentioned before, the way *pytest* resolves the fixtures can be used to give our code more flexibility. In the *medium-collector* app there is a function that uploads some files to an S3 bucket using the *boto* library, this is the function `upload_files`, which looks somewhat like this:

```python
def upload_files(file, bucket):
    client = boto3.client(
        "s3",
        aws_access_key_id=config("ACCESS_KEY"),
        aws_secret_access_key=config("SECRET_KEY"),
        region_name="eu-west-2",
    )
    client.upload_file(str(file), bucket, file.name)2
```

Of course, I do not want to keep contacting AWS every time I run the tests; here is where the library `moto`  comes to the rescue. In the word of their creators: *"Moto is a library that allows your tests to mock out AWS Services easily."*. The way they suggest you use it is as a context manager:

```python
def test_my_model_save():
    with mock_s3():
        conn = boto3.resource('s3', region_name='us-east-1')
```

To test our function, we need two things before we can actually call `upload_files` test it:

 1. Mock S3; we don't want to talk with AWS in our unit tests,
 2. Have an existing bucket; our code assumes the bucket already exists

To achieve both things with a fixture, we could have something like this:

```python
@pytest.fixture
def bucket():
   return "my_special_bucket"

@pytest.fixture
def mock_storage(bucket):
    @contextmanager
    def inner(create_bucket=True):
        with mock_s3():
            conn = boto3.client("s3", region_name="eu-east-1")
            if create_bucket:
                conn.create_bucket(Bucket=bucket)
            yield
    return inner
```

The fixture is, in reality, a function (`inner`) that thanks to the decorator `contextmanager` acts as a context manager (we can call `with` on it).  In terms of the contents of the function, you can see that we are using `mock_s3` as recommended by the developers of *moto*, inside the context we create a *boto3* client, then, depending on a parameter we create or not a bucket. And lastly, as we are treating this function as a context manager, we `yield`. 

Also, not sure if you noticed it, but `mock_storage` takes in another fixture as an argument (`bucket` in this case). That is another excellent feature of *pytest*, it allows us to create some dependencies within our fixtures, and it solves them for us before executing our tests.

Now, we are ready to test our `upload_files` function with this test:

```python
def test_upload_files(bucket, mock_storage):
    with mock_storage(create_bucket=True):
        upload_files(files_path)
        client = boto3.client("s3", region_name="eu-east-1")
        contents = client.list_objects(Bucket=bucket)["Contents"]
    assert len(contents) == 1
```

## Practice!  

I woud have liked to prepare some sort of notebook or some other interactive environment you could use to play around with the tests, but I firmly believe that, for this topic it is probably better to get your hands on some real code. I encourage you to download the [*medium-collector* repo](https://github.com/fferegrino/medium-collector) app and run the tests.

## Going beyond unit tests  
Even though *pytest* is great for unit testing, nothing stops us from using it for other, more complex, tests such as integration, or even end-to-end tests. With tools like Docker, localstack and other plugins, it is possible to come up with a powerful testing framework for all your Python projects. In a future post I will detail how you can grasp these tools to create a full end-to-end test using *pytest*, so make sure you are following me either here or [at twitter @io_exception](https://twitter.com/io_exception).
