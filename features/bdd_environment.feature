Feature: BDD environment verification
  As a test automation team
  I want to verify that Behave is correctly configured
  So that BDD scenarios can be executed over the test project

  Scenario: The BDD environment is operational
    Given a working BDD setup
    When the engine processes this scenario
    Then the scenario passes successfully