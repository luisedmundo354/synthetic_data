Feature: ComputeShares
  This describes the expected behavior for the Second Amendment template

  Background:
    Given the default contract

  Scenario: The clause should compute the number of shares to issue
    When it receives the default request
    Then it should respond with
"""
{
    "$class": "secondamendment.ComputeSharesResponse",
    "shares": 500000
}
"""
