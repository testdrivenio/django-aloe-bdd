from aloe import before, step, world
from aloe.tools import guess_types
from aloe_django.steps.models import get_model, reset_sequence, writes_models
from nose.tools import assert_count_equal, assert_dict_equal, assert_true

from django.contrib.auth.models import User
from django.test.client import Client

from ..models import Friendship


@before.each_feature
def before_each_feature(feature):
    world.client = Client()


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


@step('I empty the "([^"]+)" table')
def step_empty_table(self, model_name):
    model_class = get_model(model_name)
    model_class.objects.all().delete()
    reset_sequence(model_class)


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


@step('I create the following friendships:')
def step_create_friendships(self):
    Friendship.objects.bulk_create([
        Friendship(
            id=data['id'],
            user1=User.objects.get(id=data['user1']),
            user2=User.objects.get(id=data['user2'])
        ) for data in guess_types(self.hashes)
    ])


@step('I create the following "([^"]+)" data:')
def step_create_data(self, model_name):
    model_class = get_model(model_name)
    for data in guess_types(self.hashes):
        fields = {}
        for field_name, field_value in data.items():
            field = model_class._meta.get_field(field_name)
            field_value = field.related_model.objects.get(id=field_value) if field.many_to_one else None
            fields[field_name] = field_value
        model_class.objects.create(**fields)


@step('I create a friendship with the following data:')
def step_create_friendship(self):
    world.response = world.client.post('/friendships/', guess_types(self.hashes)[0])


@step('I add the following user as a friend:')
def step_add_friend(self):
    world.response = world.client.post('/friends/', guess_types(self.hashes)[0])
