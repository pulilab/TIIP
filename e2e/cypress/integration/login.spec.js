describe("Basic interactions test", function () {
  before(function () {
    cy.logIn();
  });

  after(function () {
    cy.logOut();
  });

  it("Basic UI items check", function () {
    cy.log("UI checkup");
    cy.visit("/en/-/inventory/list?country=1", {
      headers: {},
    });
    cy.get("[data-id=portfolioLink]").contains("Innovation Portfolios");
  });
});
