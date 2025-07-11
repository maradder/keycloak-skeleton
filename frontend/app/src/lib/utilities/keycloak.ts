import Keycloak from 'keycloak-js';
const VITE_AUTH_SERVER_BASE_URL = import.meta.env.VITE_AUTH_SERVER_BASE_URL || 'http://localhost:3000';

// Keycloak configuration
const keycloakConfig = {
  url: `${VITE_AUTH_SERVER_BASE_URL}`,
  realm: 'testrealm',
  clientId: 'test-client-id',
};

// Create Keycloak instance
const keycloak = new Keycloak(keycloakConfig);

export default keycloak;

