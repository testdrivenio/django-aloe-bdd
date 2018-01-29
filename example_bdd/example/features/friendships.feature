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
      | id | user1 | user2 | status   |
      | 1  | 1     | 2     | ACCEPTED |

    # Annie and Brian are now friends.

    When I get a list of friends

    Then I see the following response data:
      | id | email             | username |
      | 2  | brian@example.com | Brian    |

  Scenario: A user with no friends sees an empty list

    Given I empty the "Friendship" table

    # Annie has no friends.

    When I get a list of friends

    Then I see the following response data:
      | id | email | username |

  Scenario: A user with no accepted friendship requests sees an empty list

    Given I empty the "Friendship" table

    And I create the following friendships:
      | id | user1 | user2 | status   |
      | 1  | 1     | 2     | PENDING  |
      | 2  | 1     | 3     | REJECTED |

    # No one has accepted Annie's friend requests.

    When I get a list of friends

    Then I see the following response data:
      | id | email | username |

  Scenario: A user can request a friendship with another user.

    Given I empty the "Friendship" table

#    When I request a friendship with "Brian"

    When I request the following friendship:
      | user1 | user2 |
      | 1     | 2     |

    Then I see the following response data:
      | id | user1 | user2 | status  |
      | 3  | 1     | 2     | PENDING |

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
