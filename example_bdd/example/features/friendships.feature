Feature: Friendships

  Background:

    Given I empty the "Users" table

    And I create the following users:
      | id | email             | username | password  |
      | 1  | annie@example.com | Annie    | pAssw0rd! |
      | 2  | brian@example.com | Brian    | pAssw0rd! |
      | 3  | casey@example.com | Casey    | pAssw0rd! |
      | 4  | david@example.com | David    | pAssw0rd! |

    When I log in with username "Annie" and password "pAssw0rd!"

    Then I am logged in

  Scenario: 1. A user can get a list of friends

    Given I empty the "Friendship" table

#    And I create the following "Friendship" data:
#      | id | user1 | user2 |
#      | 1  | 1     | 2     |

    And I create the following friendships:
      | id | user1 | user2 |
      | 1  | 1     | 2     |

    # Annie and Brian are now friends.

    When I get a list of friends

    Then I see the following response data:
      | id | email             | username |
      | 2  | brian@example.com | Brian    |

  Scenario: 2. A user can create a friendship with another user

    Given I empty the "Friendship" table

    When I create a friendship with the following data:
      | user1 | user2 |
      | 1     | 2     |

    Then I see the following response data:
      | id | user1 | user2 |
      | 2  | 1     | 2     |

  Scenario: 3. A user cannot create a friendship with himself/herself

    Given I empty the "Friendship" table

    When I create a friendship with the following data:
      | user1 | user2 |
      | 1     | 1     |

    Then I see the following response data:
      | detail                                        |
      | You cannot create a friendship with yourself. |

  Scenario: 4. A user cannot create a new friendship with an existing friend

    Given I empty the "Friendship" table

    And I create the following friendships:
      | id | user1 | user2 |
      | 1  | 1     | 2     |

    When I create a friendship with the following data:
      | user1 | user2 |
      | 1     | 2     |

    Then I see the following response data:
      | detail                                                      |
      | You cannot create a new friendship with an existing friend. |
