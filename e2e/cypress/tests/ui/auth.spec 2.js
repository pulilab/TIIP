describe("User should Sign-up and Login", function () {
  before(function () {
    cy.server();
  });

  after(function () {
    cy.logout();
  });

  it("should redirect unauthenticated user to login page", function () {
    cy.visit("/");
    cy.location("pathname").should("equal", "/en/auth");
    cy.visualSnapshot("Redirect to Login");
  });

  it("should Basic UI items check", function () {
    cy.login(Cypress.env("testUser"), Cypress.env("testPw"));
    cy.visit("/en/-/inventory/list?country=1", {
      headers: {},
    });
    cy.getBySel("menu-portfolio-link").contains("Innovation Portfolios");
  });
});
