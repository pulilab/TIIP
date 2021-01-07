describe('End to end tests', function() {

  it('Failed log in test', function() {
    cy.log('Failed log in test');
    cy.visit(Cypress.env('login_url'));
    cy.get(':nth-child(1) > :nth-child(2) > div > input').type('pulitest@pulilab.com');
    cy.get(':nth-child(2) > :nth-child(2) > :nth-child(1) > input').type('puli12345');
    cy.get('.el-button--medium > span > span').click();
    cy.get('.el-form').submit();
    cy.get(':nth-child(2) > :nth-child(2) > :nth-child(2)').contains('Unable to log in with provided credentials.');
  })
});
