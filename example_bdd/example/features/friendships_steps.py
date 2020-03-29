from aloe import before, step, world
from aloe.tools import guess_types
from aloe_django.steps.models import get_model
from nose.tools import assert_true, assert_list_equal, assert_dict_equal
from rest_framework.test import APIClient

from django.contrib.auth.models import User

from ..models import Friendship


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


@step('I get a list of friends')
def step_get_friends(self):
    world.response = world.client.get('/friends/')


@step('I see the following response data:')
def step_confirm_response_data(self):
    response = world.response.json()
    if isinstance(response, list):
        assert_list_equal(guess_types(self.hashes), response)
    else:
        assert_dict_equal(guess_types(self.hashes)[0], response)


@step('I request the following friendship:')
def step_request_friendship(self):
    world.response = world.client.post('/friendship-requests/', data=guess_types(self.hashes[0]))


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
