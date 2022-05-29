---
layout: post
language: en
original_url: https://dev.to/fferegrino/reading-emails-with-python-4o72
title: Reading emails with Python
short_summary: So you've got a bunch of emails ready to be processed, but how?
date: 2020-01-10 10:00:00
tags: python, medium, email
---
A while ago I wanted to create a dataset that consisted of Medium blog posts, however, medium does not make it easy for web scrapers to work on their side, at least when it comes to discover posts. However, they offer a daily summary of some posts highlighted, this is delivered every day by email under the subject "Medium Daily Digest.

With this in mind, I registered [many accounts](https://gizmodo.com/how-to-use-the-infinite-number-of-email-addresses-gmail-1609458192) (each one of them with different interests) to get a somewhat diverse pool of posts, delivered directly to my inbox:

![A Gmail inbox filled with Medium Daily Digest emails](https://thepracticaldev.s3.amazonaws.com/i/efh6ro2ua23lcl614tjv.png)

Once I gathered enough emails, I [downloaded them](https://support.google.com/accounts/answer/3024190?hl=en) in a standard format known as [MBOX](https://en.wikipedia.org/wiki/Mbox) which I saved to a file named `inbox.mbox`.

As you may have guessed, Python offers a way to open this file through the use of its native API:

```python
import mailbox

inbox = mailbox.mbox('inbox.mbox')
```

Once opened, the `inbox` variable behaves pretty much like a dictionary, except that when iterated it returns the values, rather than the keys, where each value is an object of type `mailbox.mboxMessage`. This type offers the possibility of accessing some of the message properties like a dictionary:

```python
for message in inbox:
    print(message["to"])
    print(message["from"])
    print(message["subject"])
```

Something that is not uncommon is to have subjects that are `utf8` encoded, and look like this: `=?UTF-8?B?SXTigJlzIFRpbWUgdG8gTGVhdmUgU2FuIEZyYW5jaXNjbyB8IFN1bmlsIFJhamFyYW1hbiBpbiBUaGUgQm9sZCBJdGFsaWM=?=`. Before you start thinking about how to decode this string, let me tell you that Python already has the solution in the function `decode_header`, that returns a list of 2-tuples, where the first element of each tuple is a bytestring  (or just string when it is possible) and the second element is the encoding.

Beware that some subjects are a combination of `utf8`-encoded and non-encoded strings, like this: `=?UTF-8?B?VGhlcmXigJlz?= more to the story`. So to make my life easier, I came up with the following function that uses the above decoder:

```python
from email.header import decode_header

def get_subject(subject):
    subject_parts = []
    subjects = decode_header(subject)
    for content, encoding in subjects:
        try: 
            subject_parts.append(content.decode(encoding or "utf8"))
        except:
            subject_parts.append(content)
        
    return "".join(subject_parts)

get_subject("=?UTF-8?B?VGhlcmXigJlz?= more to the story")
# Output: 'There’s more to the story'
```

Once the subject has been parsed, we can move on to the content of the email. We can access this by using the method `get_payload()` that returns a list of `email.message.Message`. Now, it returns a list because an email can have different content types, most commonly there will be an email that should be displayed in plain text and one that contains HTML to be rendered in a browser.  

For the sake of simplicity, let's work with the plain text email, the HTML version is just as easy, specially if you use something like [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/).

```python
parts = { part.get_content_type(): part for part in inbox[0].get_payload() }

plain_content = parts["text/plain"]
```

To access the content of the email all you need to do now is to call the method `get_payload()` again, but this time in the selected content type. This time you'll get a string:

```python
print(plain_content.get_payload())
```

The output is something like the following:

```text
Today's highlights

It's Time to Leave San Francisco (https://medium.com/@subes01/its-time-to-l=
eave-san-francisco-2a5a74f42433?source=3Demail-199ea03185b2-1573178226124-d=
igest.reader------0-59------------------c89076aa_3fad_44f0_a28d_516f3993deb=
9-1-----&sectionName=3Dtop)

...
```  

If you notice, there is something going on with the email... there are some `=` extras in there. You may already be thinking on ways to remove those extra symbols and make the message fully readable, but hey: Python to the rescue.

The way emails are encoded is known as [QP encoding](https://en.wikipedia.org/wiki/Quoted-printable), and Python has an out-of-the-box way to deal with it in the module `quopri`:  

```python
import quopri

decoded = quopri.decodestring(plain_content.get_payload())

print(decoded.decode("utf8"))
```

With the output being, this time in a single line, without the `=`:  

```text
Today's highlights

It's Time to Leave San Francisco (https://medium.com/@subes01/its-time-to-leave-san-francisco-2a5a74f42433?source=email-199ea03185b2-1573178226124-digest.reader------0-59------------------c89076aa_3fad_44f0_a28d_516f3993deb9-1-----&sectionName=top)

...
```

And that is pretty much it, there is still much to do on my way to create a medium dataset, but I just wanted to publish this as I spent some time figuring things out and I thought I could share some of what I learned. I have uploaded the code I used for this post to both [GitHub](https://github.com/python-stuff/medium-email) and a [Binder Notebook](https://mybinder.org/v2/gh/python-stuff/medium-email/master), ready for you to explore.

If you have any questions do not hesitate to contact me on [Twitter @feregri_no](https://twitter.com/feregri_no) or to leave a comment below :)