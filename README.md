# pht-payer-invariants
Security Invariants for your payer account

## What this does

This repo contains a sample Permissions Boundary to prevent users in an Organization Management Account (aka payer) from being able to do anything dangerous. These are what we'd define as [security invariants](https://www.primeharbor.com/blog/security-invariants/) - security conditions that should _always_ be true.

AWS would tell you that you shouldn't be giving anyone access to the payer account, so the need for invariants should be minimal. However that doesn't reflect the reality that AWS never protected it's customers from themselves. They never prevented the enabling of Organizations or Control Tower in an account with existing workloads. I would say this is a failure of Customer Obsession and demonstrates Security is not the Top Priority. AWS would hide behind shared-responsibility and blame the customer.

The permission boundary policy is applied to all of the users and roles in your payer account. The InvariantEnforcer cloudformation template deploys a Lambda Function that is triggered on any EventBridge rule to ensure all newly created IAM Roles and Users have the permission boundary, and that if any user removes the boundary, it is immediately re-added.


## Deploying

This is done in three steps.
1. Create the Permissions Boundary IAM Policy
2. Deploy the Invariant Enforcer Cloudformation stack
3. Force apply the Permissions Boundary to all existing principals in the account.

First, create a `vars.txt` file similar to `[sample_vars.txt](sample_vars.txt)` These Roles should reflect the existing roles in your environment.

Next deploy the boundary policy with the command:
```bash
make create-boundary VARFILE=my_vars.txt
```

Once the policy exists, we can deploy the enforcer
```
make create-enforcer
```

Finally, once the enforcer is in place, apply the boundary to all the Users & Roles
```
make force-attachment
```

You can override the default settings by passing these parameters on the Makefile line:

    ADMIN_ROLE ?= AWSReservedSSO_AdministratorAccess
    VARFILE ?= vars.txt
    STACK_NAME ?= InvariantEnforcerStack
    PERM_BOUNDARY_NAME ?= PayerPermissionsBoundary

## Updating

You can update the boundary policy with the command
```bash
make update-boundary
```

If you need to update the enforcer
```
make update-enforcer
```
