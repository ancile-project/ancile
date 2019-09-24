# How to create a new application? 

Create users: Admin, Developer, Users 

1. Login as an *Admin*:

Register Ancile app on the provider's website (Google, Github, etc) note down `client_id` and `client_secret`.
    * Pick a `provider_name`, look at existing AncileLib modules, if you create a provider with the same name as the existing module, you will get automatic fetching of tokens when calling fetch functions.
    
    * Make sure that Ancile runs using `run_prod_server.sh`
    
    * For callback URL use: `{ancile_url}/oauth/{provider_name}/callback`

Register the new provider: `Admin->Providers->Add Provider`
    * Use `client_id`, `client_secret` obtained above
    * Use the same `provider_name`

2. Login as an *Developer*:

Add new application through the Developer console

3. Login as an *User*:

Add a provider by logging through the provider

4. Login as an *Admin*:

Add a policy for the User and the App.
