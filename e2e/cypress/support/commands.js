// ***********************************************
// This example commands.js shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************
//
//
// -- This is a parent command --
// Cypress.Commands.add("login", (email, password) => { ... })
//
//
// -- This is a child command --
// Cypress.Commands.add("drag", { prevSubject: 'element'}, (subject, options) => { ... })
//
//
// -- This is a dual command --
// Cypress.Commands.add("dismiss", { prevSubject: 'optional'}, (subject, options) => { ... })
//
//
// -- This is will overwrite an existing command --
// Cypress.Commands.overwrite("visit", (originalFn, url, options) => { ... })


Cypress.Commands.add('signUp', () => {
  cy.visit(Cypress.env('server'));
  cy.randomAlphaNumeric(10).then((response) => {
    Cypress.env('testUser', "cypress_test_user_" + response + "@example.com");  // save user to env
    cy.get('input[id="email"]').type(Cypress.env('testUser'));
    cy.get('input[id="password"]').type('puli1234');
    cy.get('input[id="passwordAgain"]').type('puli1234');
    cy.contains('Sign up now').click();
    cy.location('pathname', {timeout: 5000}).should('include', '/edit-profile');
  });
});

Cypress.Commands.add('logIn', () => {
    cy.visit(Cypress.env('login_url'));
    cy.get(':nth-child(1) > :nth-child(2) > div > input').type(Cypress.env('test_user'));
    cy.get(':nth-child(2) > :nth-child(2) > :nth-child(1) > input').type(Cypress.env('test_pw'));
    cy.get('.el-form').submit();
    cy.url().should('include', Cypress.env('server') + 'en/-/inventory/list?country=')
    cy.get(':nth-child(1) > :nth-child(1) > :nth-child(6) > :nth-child(1) > :nth-child(2) > span')
        .contains('Puli Test User');
})

Cypress.Commands.add('logOut', () => {
    cy.get(':nth-child(2) > :nth-child(1) > :nth-child(1) > :nth-child(6) > :nth-child(1) > button').click();
    cy.get(':nth-child(4) > button').click();
    // These are not quite stable TODO: figure out a way to do it better!
    // cy.url().should('include', Cypress.env('server') + 'en/auth')
    // cy.get(':nth-child(3) > :nth-child(1) > div > button > :nth-child(1) > span').contains('Login');
});
  // cy.contains("Logout").click();

Cypress.Commands.add('randomAlphaNumeric', (length) => {
  const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  let charactersLength = characters.length;
  return Array.from({length: length}, () => {
    return characters.charAt(Math.floor(Math.random() * charactersLength));
  }).join('');
});
