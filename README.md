# General Info
Client is built on Vue 3
Server is built on node ~18
Preferably server to be built on flask

# How to deploy
This file explains steps that need to be taken in order to deploy the project.

## Prerequisites
### Google
This skeleton uses google based SMTP emailing system.
It is necessary to create a gmail account, set up 2fa, and then an app password.
After set up, pass email and password to .env file of the server.

### Stripe
This skeleton uses Stripe for payment system.
It is necessary to create two products, with each having a monthly price and yearly price.
After set up, pass prices to .env file of the server, as well as stripe and webhook keys.
Note that webhook keys differ between development and deployment.

### Supabase
This skeleton uses Supabase for db management, as well as one click authentication.
It is necessary to create a project within Supabase, set up necessary tables, and activate authentication methods to selected providers. 
It is also required to set up redirect URL that points to the the app/handle-supabase route after authentication.
After set up, pass supabase URL and key to .env file of the server.

## Preparation
### Client
The Vue-based client of this skeleton must be built after successful development with <code>npm run build</code>. The <code>dist</code> folder created will be used by the server afterwards.
Before building, make sure that the <code>config.js</code> file located within client/src has the specified code:

<code>
<p>const dev = {apiUrl: 'http://localhost:5000', webUrl: 'http://localhost:8080'};</p>
<p>// const prod = {apiUrl: 'http://localhost:5000', webUrl: 'http://localhost:5000'};</p>
<p>const prod = {apiUrl: 'https://delpoy.com', webUrl: 'https://delpoy.com'};</p>
</code>

The commented-out line represents testing the deployment version within localhost.

### Server
The server is already configured to have access to the <code>dist</code> folder, therefore no action is needed on its side.

### Docker
Dockerizing the app requires transferring the required directories into the /app folder, as well as installing all necessary node modules for the server. The Dockerfile is already configured to do all that, and run the server on the exposed 5000 port.

## Deployment
Having <b>onrender.com</b> as hosting platform of preference, the deployment is done there.
The flow is relatively straightforward, with the requirement being connecting the repo to render.
The pricing plan depends on the state of the deployment, but for production grade the <b>standard</b> plan should be fine.
Environmet variables should be supplied to the service, as well as the path to the docker file, which is currently set by default.

<code></code>