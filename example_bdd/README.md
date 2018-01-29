Imagine you are a Django developer building a social network for a lean startup. The CEO is pressuring your team for an MVP. The engineers have agreed to build the product using behavior-driven development (BDD) to deliver fast and efficient results. The product owner gives you the first feature request, and following the practice of all good programming methodologies, you begin the BDD process by writing a test. Next you code a bit of functionality to make your test pass and you consider your design. The last step requires you to analyze the feature itself. Does it belong in your app?

We can't answer that question for you, but we can teach you when to ask it. In the following tutorial, we walk you through the BDD development cycle by programming an example feature using Django and Aloe. Follow along to learn how you can use the BDD process to help catch and fix poor designs quickly while programming a stable app.

## Objectives

By the time you complete this tutorial, you should:
- Have a basic understanding of business-driven development
- Have a general idea of how to implement BDD in a new project
- Be able to test your Django applications using Aloe

## Project Setup

```
(venv) $ pip install django djangorestframework aloe_django
(venv) $ django-admin startproject example_bdd
(venv) $ cd example_bdd
(venv) $ python manage.py startapp example
```

## Brief Overview of BDD

## Your First Feature Request

"Users should be able to log into the app and see a list of their friends." That's how your product manager starts the conversation about the app's first feature. It's not much but you can use it to write a test. He's actually requesting two pieces of functionality--user authentication and the ability to form relationships between users. Here's a rule of thumb: treat a conjunction like a beacon warning you against trying to test too many things at once. If you ever see an "and" or an "or" in a test statement, you should break that test into smaller ones. 

With that truism in mind you take the first half of the feature request and write a test scenario: _a user can log into the app_. In order to support user authentication, your app must store user credentials and give users a way to access their data with those credentials. Here's how you translate those criteria into an Aloe _.feature_ file.

**example/features/friendships.feature**

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

You run `python manage.py harvest` and see the following output.

```
nosetests --verbosity=1
Creating test database for alias 'default'...
E
======================================================================
ERROR: A user can log into the app (example.features.friendships: Friendships)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/parentj/.virtualenvs/blog-aloe-bdd/lib/python3.6/site-packages/aloe/registry.py", line 161, in wrapped
    return function(*args, **kwargs)
  File "/Users/parentj/Projects/blog-aloe-bdd/example_bdd/example/features/friendships.feature", line 5, in A user can log into the app
    Given I empty the "User" table
  File "/Users/parentj/.virtualenvs/blog-aloe-bdd/lib/python3.6/site-packages/aloe/registry.py", line 161, in wrapped
    return function(*args, **kwargs)
  File "/Users/parentj/.virtualenvs/blog-aloe-bdd/lib/python3.6/site-packages/aloe/exceptions.py", line 61, in undefined_step
    raise NoDefinitionFound(step)
aloe.exceptions.NoDefinitionFound: The step r"Given I empty the "User" table" is not defined

----------------------------------------------------------------------
Ran 1 test in 0.509s

FAILED (errors=1)
Destroying test database for alias 'default'...
```

**example/features/friendships_steps.py**

```python
from aloe import before, step, world
from aloe.tools import guess_types
from aloe_django.steps.models import get_model
from nose.tools import assert_true

from django.contrib.auth.models import User

from rest_framework.test import APIClient


@before.each_feature
def before_each_feature(feature):
    world.client = APIClient()


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

```
python manage.py harvest
```

```
nosetests --verbosity=1
Creating test database for alias 'default'...
.
----------------------------------------------------------------------
Ran 1 test in 0.512s

OK
Destroying test database for alias 'default'...
```

Write a test scenario for the second part of the feature request: _a user can see a list of friends_.

**example/features/friendship.feature**

```gherkin
Scenario: A user can see a list of friends

  Given I empty the "Friendship" table

  When I get a list of friends

  Then I see the following response data:
    | id | email | username |
```

Before you run the Aloe test suite, modify the first scenario to use the keyword `Background` instead of `Scenario`. Background is a special type of scenario that is run once before every block defined by `Scenario` in the _Feature_ file. Every scenario needs to start with a clean slate and using `Background` refreshes the data every time it is run.

**example/features/friendship.feature**

```gherkin
Feature: Friendships

  Background: Set up common data

    Given I empty the "User" table

    And I create the following users:
      | id | email             | username | password  |
      | 1  | annie@example.com | Annie    | pAssw0rd! |
      | 2  | brian@example.com | Brian    | pAssw0rd! |
      | 3  | casey@example.com | Casey    | pAssw0rd! |

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
    user1 = models.ForeignKey(
      settings.AUTH_USER_MODEL, 
      on_delete=models.CASCADE, 
      related_name='user1_friendships'
    )
    user2 = models.ForeignKey(
      settings.AUTH_USER_MODEL, 
      on_delete=models.CASCADE, 
      related_name='user2_friendships'
    )
```

Then you make a migration.

```
python manage.py makemigrations
python manage.py migrate
```

Next, you create a new test step for the `I create the following friendships:` statement.

**example/features/friendships_steps.py**

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

First, you create a serializer to handle the representation of the `User` resource.

**example/serializers.py**

```python
from django.contrib.auth.models import User
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username',)
        read_only_fields = fields
```

Next, you create a manager to handle table-level functionality for your `Friendship` model.

**example/models.py**

```python
class FriendshipManager(models.Manager):
    def friends(self, user):
        """Get all users that are friends with the specified user."""
        # Get all friendships that involve the specified user.
        friendships = self.get_queryset().select_related(
            'user1', 'user2'
        ).filter(
            Q(user1=user) |
            Q(user2=user)
        )

        def other_user(friendship):
            if friendship.user1 == user:
                return friendship.user2
            return friendship.user1

        return map(other_user, friendships)
```

Add `from django.db.models import Q` and add `objects = FriendshipManager()` to the `Friendship` model.

Then, you create a simple `ListAPIView` to return a JSON-serialized representation of your `User` resources.

**example/views.py**

```python
from rest_framework.generics import ListAPIView
from .models import Friendship
from .serializers import UserSerializer


class FriendsView(ListAPIView):
    serializer_class = UserSerializer

    def get_queryset(self):
        return Friendship.objects.friends(self.request.user)
```

Finally, you add a URL path.

**example_bdd/urls.py**

```python
from django.urls import path

from example.views import FriendsView

urlpatterns = [
    path('friends/', FriendsView.as_view(), name='friends'),
]
```

Create the remaining Python step functions.

**example/features/friendship_steps.py**

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

```
python manage.py harvest
```

Add one more test scenario.

**example/features/friendship.feature**

```gherkin
Scenario: A user with no friends sees an empty list

  Given I empty the "Friendship" table

  # Annie has no friends.

  When I get a list of friends

  Then I see the following response data:
    | id | email | username |
```

New feature:

"A user should be able to add another user as a friend."

**example/features/friendship.feature**

```gherkin
Scenario: A user can add a friend

  Given I empty the "Friendship" table

  When I add the following friendship:
    | user1 | user2 |
    | 1     | 2     |

  Then I see the following rows in the "Friendship" table:
    | user1 | user2 |
    | 1     | 2     |
```

**example/features/friendship_steps.py**

```python
@step('I add the following friendship:')
def step_add_friendship(self):
    world.response = world.client.post('/friendship/', data=guess_types(self.hashes[0]))


@step('I see the following rows in the "([^"]+)" table:')
def step_confirm_table(self, model_name):
    model_class = get_model(model_name)
    for data in guess_types(self.hashes):
        has_row = model_class.objects.filter(**data).exists()
        assert_true(has_row)
```

You extend the manager and do some refactoring.

**example/models.py**

```python
class FriendshipManager(models.Manager):
    def friendships(self, user):
        """Get all friendships that involve the specified user."""
        return self.get_queryset().select_related(
            'user1', 'user2'
        ).filter(
            Q(user1=user) |
            Q(user2=user)
        )

    def friends(self, user):
        """Get all users that are friends with the specified user."""
        friendships = self.friendships(user)

        def other_user(friendship):
            if friendship.user1 == user:
                return friendship.user2
            return friendship.user1

        return map(other_user, friendships)
```

You add a new serializer to render the `Friendship` resources.

**example/serializers.py**

```python
class FriendshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Friendship
        fields = ('id', 'user1', 'user2', 'status',)
        read_only_fields = ('id',)
```

You add a new view.

**example/views.py**

```python
class FriendshipsView(ModelViewSet):
    serializer_class = FriendshipSerializer

    def get_queryset(self):
        return Friendship.objects.friendships(self.request.user)
```

You add a new URL.

**example/urls.py**

```python
path('friendships/', FriendshipsView.as_view({'post': 'create'})),
```

Your code works: a user can add another user as a friend. This isn't ideal behavior. A user should not be able to add any user as a friend. That other user might not want to be friends.

"A user should be able to request a friendship with another user."

Replace your previous scenario with this one.

**example/features/friendship.feature**

```gherkin
Scenario: A user can request a friendship with another user

  Given I empty the "Friendship" table

  When I request the following friendship:
    | user1 | user2 |
    | 1     | 2     |

  Then I see the following response data:
    | id | user1 | user2 | status  |
    | 3  | 1     | 2     | PENDING |
```

Refactor your test step.

**example/features/friendship_steps.py**

```python
@step('I request the following friendship:')
def step_request_friendship(self):
    world.response = world.client.post('/friendship-requests/', data=guess_types(self.hashes[0]))
```

Add a new `status` field to the `Friendship` model.

**example/models.py**

```python
class Friendship(models.Model):
    PENDING = 'PENDING'
    ACCEPTED = 'ACCEPTED'
    REJECTED = 'REJECTED'
    STATUSES = (
      (PENDING, PENDING),
      (ACCEPTED, ACCEPTED),
      (REJECTED, REJECTED),
    )
    objects = FriendshipManager()
    user1 = models.ForeignKey(
      settings.AUTH_USER_MODEL,
      on_delete=models.CASCADE,
      related_name='user1_friendships'
    )
    user2 = models.ForeignKey(
      settings.AUTH_USER_MODEL,
      on_delete=models.CASCADE,
      related_name='user2_friendships'
    )
    status = models.CharField(max_length=8, choices=STATUSES, default=PENDING)
```

Make a migration and migrate the database.

```
python manage.py makemigrations
python manage.py migrate
```

Rename the view.

**example/views.py**

```python
class FriendshipRequestsView(ModelViewSet):
    serializer_class = FriendshipSerializer

    def get_queryset(self):
        return Friendship.objects.friendships(self.request.user)
```

You refactor the URL path.

**example/urls.py**

```python
path('friendship-requests/', FriendshipRequestsView.as_view({'post': 'create'}))
```

Import `from example.views import FriendshipRequestsView`.

You add new test scenarios.

**example/features/friendship.feature**

```gherkin
Scenario: A user can accept a friendship request

  Given I empty the "Friendship" table

  And I create the following friendships:
    | id | user1 | user2 | status  |
    | 1  | 2     | 1     | PENDING |

  When I accept the friendship request with ID "1"

  Then I see the following response data:
    | id | user1 | user2 | status   |
    | 1  | 2     | 1     | ACCEPTED |

Scenario: A user can reject a friendship request

  Given I empty the "Friendship" table

  And I create the following friendships:
    | id | user1 | user2 | status  |
    | 1  | 2     | 1     | PENDING |

  When I reject the friendship request with ID "1"

  Then I see the following response data:
    | id | user1 | user2 | status   |
    | 1  | 2     | 1     | REJECTED |
```

You add new test steps.

**example/features/friendship_steps.py**

```python
@step('I accept the friendship request with ID "([^"]+)"')
def step_accept_friendship_request(self, pk):
    world.response = world.client.put(f'/friendship-requests/{pk}/', data={
      'status': Friendship.ACCEPTED
    })


@step('I reject the friendship request with ID "([^"]+)"')
def step_reject_friendship_request(self, pk):
    world.response = world.client.put(f'/friendship-requests/{pk}/', data={
      'status': Friendship.REJECTED
    })
```

You add a new URL path.

**example/urls.py**

```python
path('friendship-requests/<int:pk>/', FriendshipRequestsView.as_view({'put': 'partial_update'}))
```

Update `Scenario: A user can see a list of friends` like the following.

**example/features/friendship.feature**

```gherkin
Scenario: A user can see a list of friends

  Given I empty the "Friendship" table

  And I create the following friendships:
    | id | user1 | user2 | status   |
    | 1  | 1     | 2     | ACCEPTED |

  # Annie and Brian are now friends.

  When I get a list of friends

  Then I see the following response data:
    | id | email             | username |
    | 2  | brian@example.com | Brian    |
```

Add one more scenario.

**example/features/friendship.feature**

```gherkin
Scenario: A user with no accepted friendship requests sees an empty list

  Given I empty the "Friendship" table

  And I create the following friendships:
    | id | user1 | user2 | status   |
    | 1  | 1     | 2     | PENDING  |
    | 2  | 1     | 3     | REJECTED |

  When I get a list of friends

  Then I see the following response data:
    | id | email | username |
```

You edit the following step.

**example/features/friendship_steps.py**

```python
@step('I create the following friendships:')
def step_create_friendships(self):
    Friendship.objects.bulk_create([
        Friendship(
            id=data['id'],
            user1=User.objects.get(id=data['user1']),
            user2=User.objects.get(id=data['user2']),
            status=data['status']
        ) for data in guess_types(self.hashes)
    ])
```

You update the model.

**example/models.py**

```python
def friends(self, user):
    """Get all users that are friends with the specified user."""
    friendships = self.friendships(user).filter(status=Friendship.ACCEPTED)

    def other_user(friendship):
        if friendship.user1 == user:
            return friendship.user2
        return friendship.user1

    return map(other_user, friendships)
```

Feature complete!
