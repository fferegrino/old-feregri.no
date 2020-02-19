---
layout: post
language: en
original_url: https://dev.to/fferegrino/creating-an-aws-lambda-using-pipenv-2h4a
title: Creating an AWS Lambda using python
date: 2020-01-28 10:00:00
tags: aws, aws-lambda, python, pip
---
The AWS Lambdas represent one of the most common solutions when deploying serverless applications. In this post, I try to cover how to develop, package, deploy and configure a single function, that runs in somebody else's computer.

<small>Este post también está disponible en español, [da click aquí](https://dev.to/fferegrino/creando-una-lambda-en-aws-usando-pipenv-14mh) para leerlo</small>

### Developing

As we will be using Python, it is highly recommended that we create a virtual environment and enter it before continuing:

```shell
python -m venv env
source env/bin/activate
```

Then we can install the libraries we will use in our lambda, in our case the only libraries we are going to use are `requests` and `twython`:

```shell
pip install requests twython 
```

Once we have done this, we can proceed to develop our function. It is as simple as this:

```python
def lambda_handler(event, context):
    pokemon_id = event["pokemon_id"]
    response = requests.get(f"https://pokeapi.co/api/v2/pokemon/{pokemon_id}/")
    pokemon = json.loads(response.text)
    tweeted = tweet(pokemon)
    return {
        "message": f"It is {pokemon['species']['name']}!",
        "tweeted": tweeted
    }
```

The critical piece of our lambda code is the function `lambda_handler` along with its two parameters `event` and `context`; we care about the first one: it is a dictionary that contains information that we want to pass to our lambda when it gets triggered. In our case we are expecting an int, under the key `pokemon_id`, it uses this number to fetch a pokemon from the Pokéapi. Then it returns another dictionary with some "useful" information. Of course, this is a silly example, and your lambdas could do more valuable stuff.

Though our code is running on a server that we do not manage, we still have access to the environment variables of the system it is running, the function `tweet`  takes some secrets from the env vars that allow our lambda to tweet about the selected pokemon:

```python
def  tweet(pokemon):
    variables = [
        "API_KEY",
        "API_SECRET_KEY",
        "ACCESS_TOKEN",
        "ACCESS_TOKEN_SECRET"
    ]

    if  all(var in os.environ for var in variables):
        twitter = Twython(
            os.environ["API_KEY"],
            os.environ["API_SECRET_KEY"],
            os.environ["ACCESS_TOKEN"],
            os.environ["ACCESS_TOKEN_SECRET"]
        )
        twitter.update_status(status=f"It is {pokemon['species']['name']}!")
        return  True
    return  False
```
<small>[Check here](https://developer.twitter.com/en/docs/basics/authentication/oauth-1-0a/obtaining-user-access-tokens) to learn more about access tokens and secrets, though it is not necessary to continue with the rest of the tutorial.</small>

Both functions, along with their imports, can be placed in a single (or multiple files), in my case, I opted for a single file.

### Packaging

The next step is to prepare our code for upload. Now, if we had not used any other external library, we could have just pasted our code into an Amazon-provided UI; but that is not our case, we have to package our code along with our dependencies in a compressed file. 

There is one thing to consider before packaging our lambda: it is very likely that the operating system our lambda is going to be running, does not match the one we developed it on. The lambda runs [Amazon's version of Linux](https://aws.amazon.com/amazon-linux-ami/), which means that some packages may not work when executed in the lambda environment.

But not so fast, there is an easy solution: Docker! We can run a container with an image somewhat similar to the one Amazon uses. If we install our packages there, they should work without issues in AWS... and then we can zip what we installed. To enact our plan, we execute the following commands:

```shell
mkdir build
pip freeze > ./build/requirements.txt
cp *.py build
docker run --rm -v ${PWD}/build:/var/task \
    -u 0 lambci/lambda\:build-python3.7 \
    python3.7 -m pip install -t /var/task/ -r /var/task/requirements.txt
cd build && zip -r ../lambda.zip *
```
 As a quick explanation:
 
 - **mkdir build**: we create a folder called *build*  
 - **pip freeze > ./build/requirements.txt**: generate a `requirements.txt` inside our newly created folder, this file comes from our environment  
 - **cp *.py build**: copy our lambda files inside build
**docker run ...**: run the command `python3.7 -m pip install -t /var/task/ -r /var/task/requirements.txt` inside a container created with `lambci/lambda\:build-python3.7` as image, this container has the folder `build` attached as a volume under the path `/var/task/`.  
 - **cd build && zip -r ../lambda.zip \***: as a last step, compress both the environment files and our python files into the file `lambda.zip`

### Uploading

Once we have our zip, all that is left is to configure the lambda in AWS, so login into your console and head over to the lambda section, what follows is a guide using images on how to navigate the console:

![From the Services tab click the Lambda menu, it is under Compute](https://thepracticaldev.s3.amazonaws.com/i/qpq77qck8r1sfqfjipe3.png)

From there, you will see a very bright button that says "Create a function", from there, fill in the name of your lambda, and as runtime choose *Python 3.7*, remember, we are authoring from scratch too.

![Change the name of your lambda, and select the appropriate runtime](https://thepracticaldev.s3.amazonaws.com/i/gqfnf3z2rd1f0ybmw6ca.png)

The following screen shows the configuration for our lambda, what we need to do now is to navigate to the **Function code** section, where we must choose *Upload a .zip file* as *Code entry type*, and set *Handler* to the location of our `lambda_handler` function defined above, this value is something like `lambda_function.lambda_handler`, and then select the zip file our script created to be uploaded:


![Function code section](https://thepracticaldev.s3.amazonaws.com/i/m6apg8dajp743gort1f3.png)

Finally, click *Save*. Once saved the **Function code** section will change to an editor that you can then use to modify the code of your lambda. But we won't do that.

#### Configuring

If you remember correctly, our lambda can make use of environment variables, to modify them, it is necessary to navigate to the **Environment variables** section, where we need to add the variables we'll use:

![Our environment variables](https://thepracticaldev.s3.amazonaws.com/i/bjhqss38oiqryqjgl9g2.png)

Do not forget to save your work at every section change you make!

#### Testing
Lastly, if you scroll all the way back to the top, you can see that next to the *Save* button there is one that we can use to create test events, after pressing it, it will give you the option of crafting the message that your lambda will receive:

![Create the test message your lambda will receive](https://thepracticaldev.s3.amazonaws.com/i/4h117l40fu6dlfbg3s64.png)

After this step, you can save and then click test again, this time our lambda should work and execute, we can see the output of it in the panel being shown after clicking, or, if you set up the tweeting part of the lambda, by now you should be able to see a tweet from that account:

![Logs display](https://thepracticaldev.s3.amazonaws.com/i/dpu6v1zc6ttydkjzazj1.png)

![The tweet we just tweeted from our lambda](https://thepracticaldev.s3.amazonaws.com/i/3okqr3xxu062y9khz9oj.png)

And that is it, now you have a functioning lambda that is built in the same environment it will be run on. I hope you were able to follow this tutorial if you have any comments or questions, do not forget to leave them down below or to contact me on [@io_exception on twitter](https://twitter.com/io_exception/).
