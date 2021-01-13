describe('Basic interactions test', function() {
  before(function () {
    cy.logIn();
  });

  after(function () {
    cy.logOut();
  });

  it('Basic UI items check', function() {
    cy.log('UI checkup');
    // TODO get one of the FE guys to fix this, I'm stupid for JavaScript
    cy.visit(Cypress.env('url_base') + 'en/-/inventory/list?country=1', {headers: {}});
    cy.get(':nth-child(1) > :nth-child(2) > a > span').contains('Innovation Portfolios');
  });
});
