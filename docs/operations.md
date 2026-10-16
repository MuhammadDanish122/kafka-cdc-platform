# Operations

- **Environments:** Local/dev → staging → prod, promoted by Git tag. Prod needs a dry run and sign-off.
- **Runtime flags** stay per environment and are excluded from deploys.
- **Recycling:** consumers restart in batches with a hold time between batches.
- **Alerting:** Nagios checks for connectors, consumers and lag.
- **Services** run under systemd on Linux; scheduled jobs in Airflow.
