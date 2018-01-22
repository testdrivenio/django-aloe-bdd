Imagine you are a Django developer building a social network for a lean startup. The CEO is pressuring your team for an MVP. The engineers have agreed to build the product using behavior-driven development (BDD) to deliver fast and efficient results. The product owner gives you the first feature request, and following the practice of all good programming methodologies, you begin the BDD process by writing a test. Next you code a bit of functionality to make your test pass and you consider your design. The last step requires you to analyze the feature itself. Does it belong in your app?

We can't answer that question for you, but we can teach you when to ask it. In the following tutorial, we walk you through the BDD development cycle by programming an example feature using Django and Aloe. Follow along to learn how you can use the BDD process to help catch and fix poor designs quickly while programming a stable app.

## Objectives

By the time you complete this tutorial, you should:
- Have a basic understanding of business-driven development
- Have a general idea of how to implement BDD in a new project
- Be able to test your Django applications using Aloe

## Project Setup

## Brief Overview of BDD

## Your First Feature Request

"Users should be able to log into the app and see a list of their friends." That's how your product manager starts the conversation about the app's first feature. It's not much but you can use it to write a test. He's actually requesting two pieces of functionality--user authentication and the ability to form relationships between users. Here's a rule of thumb: treat a conjunction like a beacon warning you against trying to test too many things at once. If you ever see an "and" or an "or" in a test statement, you should break that test into smaller ones. 

With that truism in mind you take the first half of the feature request and write a test scenario: _a user can log into the app_. In order to support user authentication, your app must store user credentials and give users a way to access their data with those credentials. Here's how you translate those criteria into an Aloe _.feature_ file.

**features/friendships.feature**

```gherkin
Feature: Friendships

  Scenario: A user can log into the app

    Given I empty the "User" table

    And I create the following users:
      | id | email             | username | password  |
      | 1  | annie@example.com | Annie    | pAssw0rd! |

    When I log in with username "Annie" and password "pAssw0rd!"

    Then I am logged in
```

An Aloe test case is called a feature. Developers program features using two files--a _Feature_ file and a _Steps_ file. The _Feature_ file consists of statements written in plain English that describe how to configure, execute, and confirm the results of a test. Use the `Feature` keyword to label the feature and the `Scenario` keyword to define a user story that you are planning to test. In the example above, the scenario defines a series of steps that explain how to populate the _User_ database table, log a user into the app, and validate the login. All step statements must begin with one of four keywords: `Given`, `When`, `Then`, or `And`.

The _Steps_ file contains Python functions that are mapped to the _Feature_ file steps using regular expressions.

**features/friendships_steps.py**

```python
from aloe import before, step, world
from aloe.tools import guess_types
from aloe_django.steps.models import get_model
from nose.tools import assert_true

from django.contrib.auth.models import User
from django.test.client import Client


@before.each_feature
def before_each_feature(feature):
    world.client = Client()


@step('I empty the "([^"]+)" table')
def step_empty_table(self, model_name):
    get_model(model_name).objects.all().delete()


@step('I create the following users:')
def step_create_users(self):
    for user in guess_types(self.hashes):
        User.objects.create_user(**user)


@step('I log in with username "([^"]+)" and password "([^"]+)"')
def step_log_in(self, username, password):
    world.is_logged_in = world.client.login(username=username, password=password)


@step('I am logged in')
def step_confirm_log_in(self):
    assert_true(world.is_logged_in)
```

Each statement is mapped to a Python function via a `@step()` decorator. For example, `Given I empty the "User" table` will trigger the `step_empty_table()` function to run. In this case, the string `"User"` will be captured and passed to the function as the `model_name` parameter. The Aloe API includes a special global variable called `world` that can be used to store and retrieve data between test steps. Notice how the `world.is_logged_in` variable is created in `step_log_in()` and then accessed in `step_confirm_log_in()`. Lastly, Aloe also defines a special `@before` decorator to execute functions before tests run.

Run the Aloe test suite with the following command to see all tests pass.

```bash
python manage.py harvest
```

Write a test scenario for the second part of the feature request: _a user can see a list of friends_.

```gherkin
Scenario: A user can see a list of friends

  Given I empty the "Friendship" table

  When I get a list of friends

  Then I see the following response data:
    | id | email | username |
```

Before you run the Aloe test suite, modify the first scenario to use the keyword `Background` instead of `Scenario`. Background is a special type of scenario that is run once before every block defined by `Scenario` in the _Feature_ file. Every scenario needs to start with a clean slate and using `Background` refreshes the data every time it is run.

```gherkin
Feature: Friendships

  Background: Set up common data

    Given I empty the "User" table

    And I create the following users:
      | id | email             | username | password  |
      | 1  | annie@example.com | Annie    | pAssw0rd! |
      | 2  | brian@example.com | Brian    | pAssw0rd! |

    When I log in with username "Annie" and password "pAssw0rd!"

    Then I am logged in

  Scenario: A user can see a list of friends

    Given I empty the "Friendship" table

    And I create the following friendships:
      | id | user1 | user2 |
      | 1  | 1     | 2     |

    # Annie and Brian are now friends.

    When I get a list of friends

    Then I see the following response data:
      | id | email             | username |
      | 2  | brian@example.com | Brian    |
```

The new scenario clears all entries from a "Friendship" table and creates one new record to define a friendship between Annie and Brian. Then it calls an API to retrieve a list of Annie's friends and it confirms that the response data includes Brian.

You start by creating a "Friendship" database table.

**example/models.py**

```python
from django.conf import settings
from django.db import models


class Friendship(models.Model):
    user1 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user1_friendships')
    user2 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user2_friendships')
```

Then you make a migration.

```bash
python manage.py makemigrations
```

Next, you create a new test step for the `I create the following friendships:` statement.

**features/friendships_steps.py**

```python
@step('I create the following friendships:')
def step_create_friendships(self):
    Friendship.objects.bulk_create([
        Friendship(
            id=data['id'],
            user1=User.objects.get(id=data['user1']),
            user2=User.objects.get(id=data['user2'])
        ) for data in guess_types(self.hashes)
    ])
```

Add the `Friendship` model import.

```python
from ..models import Friendship
```

Create an API to get a list of the logged-in user's friends.

**example/views.py**

```python
from django.db.models import Q
from django.http import JsonResponse
from django.views import View

from .models import Friendship


class FriendsView(View):
    def get(self, request):
        # Get all friendships that involve the logged-in user.
        friendships = Friendship.objects.select_related('user1', 'user2').filter(
            Q(user1=request.user) |
            Q(user2=request.user)
        )

        # Get a list of friends.
        friends = [
            friendship.user1 
            if friendship.user2 == request.user 
            else friendship.user2 
            for friendship in friendships
        ]

        # Return a JSON-serialized list of friend data.
        return JsonResponse([{
            'id': friend.id,
            'email': friend.email,
            'username': friend.username,
        } for friend in friends], safe=False)
```

**example_bdd/urls.py**

```python
from django.urls import path

from example.views import FriendsView

urlpatterns = [
    path('friends/', FriendsView.as_view(), name='friends'),
]
```

Create the remaining Python step functions.

```python
@step('I get a list of friends')
def step_get_friends(self):
    world.response = world.client.get('/friends/')


@step('I see the following response data:')
def step_confirm_response_data(self):
    response = world.response.json()
    if isinstance(response, list):
        assert_count_equal(guess_types(self.hashes), response)
    else:
        assert_dict_equal(guess_types(self.hashes)[0], response)
```

Import the `assert_count_equal()` and `assert_dict_equal()` functions from `nose.tools`.

You run the tests and watch them pass.

```bash
python manage.py harvest
```

Add one more test scenario.

```gherkin
Scenario: A user with no friends sees an empty list

  Given I empty the "Friendship" table

  # Annie has no friends.

  When I get a list of friends

  Then I see the following response data:
    | id | email | username |
```