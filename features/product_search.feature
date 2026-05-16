# Traceability: TC-019 · RF-03

Feature: Product search
  As a Juice Shop customer
  I want to search products by keyword
  So that I can find products related to my interest

  Background:
    Given OWASP Juice Shop is running locally

  Scenario: Search existing product by keyword
    When the user searches for an existing product keyword
    Then the product catalog displays matching Apple products