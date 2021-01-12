describe('Basic interactions test', function() {
  before(function () {
    cy.logIn();
  });

  after(function () {
    cy.logOut();
  });

  it('Basic UI items check', function() {
    cy.log('UI checkup');
    cy.visit('http://localhost:3000/en/-/inventory/list?country=1', {headers: {}});
    cy.get(':nth-child(1) > :nth-child(2) > a > span').contains('Innovation Portfolios');
  });
});