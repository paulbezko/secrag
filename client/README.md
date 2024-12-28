## Install packages
# To install all packages
npm install

# To install one specific package
npm install PACKAGE

# Run client with port 8080
npm run serve

# Build client into /dist folder
npm run build



User states:
Anon New
Anon Returned
Clicked Sign Up with correct email



sign up steps

user clicks sign up button on website
post request to /onboarding-start
 - email
 - token

user clicks link in email
get request to /confirm-email
 - 

user clicks confirm after setting his password
post request to /onboarding-finish
 - token
 - password

to onboard:
user has to confirm email and password
user has to subscribe



When user accesses website -> Client checks if _a or _u exists
If yes, this.userStatus = 'Anonymous' or 'Authenticated' Welcome back
If not, Welcome to SECRAG


When user sends a message -> Client checks if this.userStatus === 'Authenticated'
If not, Client checks if _a exists. If yes, commit messages
If not, Client sets this.userStatus === 'Anonymous' -> Server generates uuid, check supabase if key exists, commit messages

user statuses:
interacted: false, confirmedEmail: false, confirmedPassword: false, subscribed: false - ''
interacted: true,  confirmedEmail: false, confirmedPassword: false, subscribed: false - 0 'anonymous'
sign up - submitted email - server sends confirmation - user clicks link in email - user directed to client
interacted: true,  confirmedEmail: true,  confirmedPassword: false, subscribed: false - 1 'verified'
interacted: true,  confirmedEmail: true,  confirmedPassword: true,  subscribed: false - 2 'registered'
interacted: true,  confirmedEmail: true,  confirmedPassword: true,  subscribed: true  - 3 'subscribed'

token only exists in interacted users
anonymous _u has following:
uuid: 418736
signed_up: False

signed_up _u has following:
uuid: 418736
signed_up: True
email: test@gmail.com



functionality checklist

signup password
confirm email
login password
reset password
sign out

delete account
sign up google
sign in google

