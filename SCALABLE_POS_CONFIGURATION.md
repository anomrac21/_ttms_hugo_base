# Scalable POS Configuration Guide

This guide explains how to configure POS systems for multiple OMG Sushi locations using a scalable, maintainable approach.

## Overview

The scalable POS configuration system allows you to:
- Manage multiple locations with independent POS configurations
- Support multiple POS providers (Loyverse, Odoo) per location
- Easily add new locations without code changes
- Maintain security through location-specific access tokens
- Scale horizontally as your business grows

## Architecture

### Location-Based Configuration

Each location has its own configuration in `data/locations.yaml`:

```yaml
locations:
  - address: "Location Address"
    city: "City Name"
    island: "Trinidad"
    subcategories: ["Restaurant", "Bar"]
    pos:
      loyverse:
        enabled: true
        provider: "loyverse"
        store_id: "{{ env `LOYVERSE_STORE_ID_LOCATION_NAME` }}"
        access_token: "{{ env `LOYVERSE_ACCESS_TOKEN_LOCATION_NAME` }}"
        # ... other config
      odoo:
        enabled: true
        provider: "odoo"
        # ... other config
```

### Environment Variable Pattern

Use a consistent naming pattern for environment variables:

```
LOYVERSE_STORE_ID_<LOCATION_ID>
LOYVERSE_ACCESS_TOKEN_<LOCATION_ID>
ODOO_API_URL_<LOCATION_ID>
ODOO_DATABASE_<LOCATION_ID>
# ... etc
```

Where `<LOCATION_ID>` is a standardized identifier (e.g., ARIAPITA, MUCURAPO, DIAMOND_VALE).

## Adding New Locations

### Step 1: Update Environment Variables

Add new environment variables to `.env`:

```bash
# New Location - Example: San Fernando
LOYVERSE_STORE_ID_SAN_FERNANDO=your_store_id_here
LOYVERSE_ACCESS_TOKEN_SAN_FERNANDO=your_access_token_here
ODOO_API_URL_SAN_FERNANDO=https://sanfernando-odoo.yourdomain.com
ODOO_DATABASE_SAN_FERNANDO=omgsushi_san_fernando
ODOO_COMPANY_ID_SAN_FERNANDO=1
ODOO_PARTNER_ID_SAN_FERNANDO=1
ODOO_POS_CONFIG_ID_SAN_FERNANDO=1
ODOO_USER_ID_SAN_FERNANDO=1
```

### Step 2: Update locations.yaml

Add the new location configuration:

```yaml
- address: "High Street, San Fernando"
  city: "San Fernando"
  island: "Trinidad"
  subcategories: 
    - Restaurant
  latlon: [10.2833,-61.4667]
  phone: 18681234567
  whatsapp: 18681234567
  orderingtables: ["Table 1", "Table 2", "Table 3", "Takeaway Only"]
  delivery:
    fooddrop: https://fooddropcaribbean.com/en/store/OMGSushi/san-fernando
  pos:
    loyverse:
      enabled: true
      provider: "loyverse"
      store_id: "{{ env `LOYVERSE_STORE_ID_SAN_FERNANDO` }}"
      access_token: "{{ env `LOYVERSE_ACCESS_TOKEN_SAN_FERNANDO` }}"
      webhook_secret: "{{ env `LOYVERSE_WEBHOOK_SECRET` }}"
      api_url: "{{ env `POS_API_URL` }}"
      sync_menu: true
      auto_process_orders: true
      fallback_to_whatsapp: true
    odoo:
      enabled: true
      provider: "odoo"
      company_id: "{{ env `ODOO_COMPANY_ID_SAN_FERNANDO` }}"
      partner_id: "{{ env `ODOO_PARTNER_ID_SAN_FERNANDO` }}"
      pos_config_id: "{{ env `ODOO_POS_CONFIG_ID_SAN_FERNANDO` }}"
      user_id: "{{ env `ODOO_USER_ID_SAN_FERNANDO` }}"
      api_url: "{{ env `ODOO_API_URL_SAN_FERNANDO` }}"
      database: "{{ env `ODOO_DATABASE_SAN_FERNANDO` }}"
      sync_menu: true
      auto_process_orders: true
      fallback_to_whatsapp: true
  opening_hours:
    mode: Auto
    sun: []
    mon:
      - type: Open
        time: "11:00"
      - type: Close
        time: "22:00"
    # ... rest of opening hours
```

### Step 3: Update POS Systems

Configure the new location in your POS systems:

#### Loyverse
1. Create a new store in Loyverse Back Office
2. Note the Store ID
3. Generate a new access token for the location
4. Configure webhooks if needed

#### Odoo
1. Create a new company/location in Odoo
2. Set up POS configuration for the location
3. Create API user with appropriate permissions
4. Note all relevant IDs (company, partner, POS config, user)

### Step 4: Deploy Configuration

Update your Kubernetes secrets and redeploy:

```bash
kubectl create secret generic omgsushi-pos-secrets \
  --from-env-file=.env \
  --namespace=omgsushi-pos \
  --dry-run=client -o yaml | kubectl apply -f -
```

## POS Provider Configuration

### Loyverse Configuration

```yaml
loyverse:
  enabled: true
  provider: "loyverse"
  store_id: "{{ env `LOYVERSE_STORE_ID_LOCATION` }}"
  access_token: "{{ env `LOYVERSE_ACCESS_TOKEN_LOCATION` }}"
  webhook_secret: "{{ env `LOYVERSE_WEBHOOK_SECRET` }}"
  api_url: "{{ env `POS_API_URL` }}"
  sync_menu: true
  auto_process_orders: true
  fallback_to_whatsapp: true
```

**Configuration Options:**
- `enabled`: Enable/disable Loyverse integration
- `store_id`: Loyverse store identifier
- `access_token`: API access token for the store
- `webhook_secret`: Secret for webhook validation
- `api_url`: Base URL for the POS integration API
- `sync_menu`: Automatically sync menu items
- `auto_process_orders`: Automatically process incoming orders
- `fallback_to_whatsapp`: Fall back to WhatsApp if POS fails

### Odoo Configuration

```yaml
odoo:
  enabled: true
  provider: "odoo"
  company_id: "{{ env `ODOO_COMPANY_ID_LOCATION` }}"
  partner_id: "{{ env `ODOO_PARTNER_ID_LOCATION` }}"
  pos_config_id: "{{ env `ODOO_POS_CONFIG_ID_LOCATION` }}"
  user_id: "{{ env `ODOO_USER_ID_LOCATION` }}"
  api_url: "{{ env `ODOO_API_URL_LOCATION` }}"
  database: "{{ env `ODOO_DATABASE_LOCATION` }}"
  sync_menu: true
  auto_process_orders: true
  fallback_to_whatsapp: true
```

**Configuration Options:**
- `enabled`: Enable/disable Odoo integration
- `company_id`: Odoo company identifier
- `partner_id`: Odoo partner/customer identifier
- `pos_config_id`: POS configuration identifier
- `user_id`: API user identifier
- `api_url`: Odoo instance URL
- `database`: Odoo database name
- Other options same as Loyverse

## Security Best Practices

### Access Token Management

1. **Location-Specific Tokens**: Use separate access tokens for each location
2. **Token Rotation**: Regularly rotate access tokens
3. **Limited Permissions**: Use tokens with minimal required permissions
4. **Secure Storage**: Store tokens in Kubernetes secrets, not in code

### Environment Variable Security

```bash
# Good: Location-specific tokens
LOYVERSE_ACCESS_TOKEN_ARIAPITA=token_for_aripita_only
LOYVERSE_ACCESS_TOKEN_MUCURAPO=token_for_mucurapo_only

# Bad: Shared token across locations
LOYVERSE_ACCESS_TOKEN=shared_token_for_all_locations
```

### Webhook Security

1. **Unique Secrets**: Use different webhook secrets per location/provider
2. **HTTPS Only**: Ensure all webhook endpoints use HTTPS
3. **Signature Validation**: Always validate webhook signatures
4. **Rate Limiting**: Implement rate limiting on webhook endpoints

## Monitoring and Maintenance

### Health Checks

Implement health checks for each location's POS integration:

```yaml
# Example health check endpoint
GET /api/health/locations/{location_id}/pos/{provider}
```

### Logging

Use structured logging with location and provider context:

```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "info",
  "location": "ARIAPITA",
  "provider": "LOYVERSE",
  "event": "order_processed",
  "order_id": "12345",
  "status": "success"
}
```

### Metrics

Track key metrics per location:
- Order processing success rate
- API response times
- Webhook delivery success rate
- Menu sync status
- POS system availability

## Troubleshooting

### Common Issues

1. **Location Not Found**
   - Verify location ID in environment variables
   - Check location configuration in `locations.yaml`
   - Ensure proper naming convention

2. **POS Provider Not Responding**
   - Check API endpoint connectivity
   - Verify access token validity
   - Review POS system logs

3. **Webhook Failures**
   - Verify webhook URL accessibility
   - Check webhook secret configuration
   - Review webhook delivery logs

### Debug Mode

Enable debug mode for troubleshooting:

```bash
DEBUG=true
LOG_LEVEL=debug
```

## Scaling Considerations

### Horizontal Scaling

- **Multiple API Instances**: Deploy multiple API service instances
- **Load Balancing**: Use Kubernetes load balancer
- **Database Scaling**: Consider database read replicas for high traffic

### Vertical Scaling

- **Resource Limits**: Set appropriate CPU/memory limits
- **Auto-scaling**: Configure horizontal pod autoscaling
- **Monitoring**: Monitor resource usage and scale accordingly

### Geographic Scaling

- **Regional Deployment**: Deploy API services closer to POS systems
- **CDN Integration**: Use CDN for static assets
- **Database Replication**: Consider multi-region database replication

## Migration Strategies

### Adding POS Providers

1. **Gradual Rollout**: Enable new provider alongside existing ones
2. **A/B Testing**: Test new provider with subset of locations
3. **Fallback Strategy**: Maintain existing provider as fallback

### Updating Configurations

1. **Blue-Green Deployment**: Deploy new configuration alongside old
2. **Canary Deployment**: Gradually roll out configuration changes
3. **Rollback Plan**: Always have a rollback strategy

## Best Practices Summary

1. **Consistent Naming**: Use consistent naming conventions for locations and variables
2. **Environment Isolation**: Keep production and staging configurations separate
3. **Documentation**: Document all configuration changes
4. **Testing**: Test configuration changes in staging environment first
5. **Monitoring**: Implement comprehensive monitoring and alerting
6. **Security**: Follow security best practices for all configurations
7. **Backup**: Regularly backup configuration and secrets
8. **Version Control**: Keep all configurations in version control
