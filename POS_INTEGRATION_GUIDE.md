# OMG Sushi POS Integration Guide

This guide explains how to integrate your OMG Sushi Hugo-based menu system with multiple POS systems using Kubernetes.

## Overview

The integration provides a seamless connection between your digital menu and POS systems (Loyverse, Odoo), allowing orders to be automatically processed in your POS while maintaining the existing WhatsApp ordering functionality.

## Features

- **Multi-POS Support**: Support for Loyverse and Odoo POS systems
- **Multi-location Support**: Handle multiple OMG Sushi locations with individual POS configurations
- **Dual Order Processing**: Orders are sent to both WhatsApp and POS systems
- **Menu Synchronization**: Sync your Hugo menu items with POS systems
- **Real-time Order Processing**: Orders are processed immediately in POS
- **Webhook Support**: Receive real-time updates from POS systems
- **Fallback System**: WhatsApp ordering continues to work if POS is unavailable
- **Kubernetes Deployment**: Scalable, containerized deployment

## OMG Sushi Locations

OMG Sushi has three locations, each with independent POS configuration:

1. **Ariapita Avenue, Port of Spain** - Restaurant & Bar
2. **Mucurapo Road, Port of Spain** - Food Truck
3. **Diamond Vale, Diego Martin** - Food Truck

## Setup Instructions

### 1. Prerequisites

- Kubernetes cluster with ingress controller
- kubectl configured for your cluster
- POS system accounts (Loyverse, Odoo, etc.)

### 2. POS System Setup

#### Loyverse Setup
1. **Create Loyverse Account**
   - Sign up at [loyverse.com](https://loyverse.com)
   - Set up your store(s) in Loyverse Back Office

2. **Generate API Access Token**
   - Go to Loyverse Back Office → Settings → Access Tokens
   - Click "Add access token"
   - Provide a name (e.g., "OMG Sushi Menu Integration")
   - Set expiration date (optional)
   - Save and copy the token

3. **Get Store IDs**
   - In Loyverse Back Office, go to Settings → General
   - Note down the Store ID for each location

#### Odoo Setup
1. **Install Odoo POS Module**
   - Ensure Point of Sale module is installed and configured
   - Set up your POS configurations for each location

2. **Create API User**
   - Create a dedicated API user with POS access
   - Note down the user ID, company ID, and partner ID

3. **Configure POS Configurations**
   - Set up individual POS configurations for each location
   - Note down the POS configuration IDs

### 3. Environment Configuration

1. **Copy Environment Template**
   ```bash
   cp env.example .env
   ```

2. **Fill in Your Values**
   Edit `.env` with your actual POS system credentials:
   ```bash
   # POS API Configuration
   POS_API_URL=https://api.omgsushi.ttmenus.com
   
   # Loyverse Configuration
   LOYVERSE_WEBHOOK_SECRET=your_actual_webhook_secret
   LOYVERSE_STORE_ID_ARIAPITA=your_actual_store_id
   LOYVERSE_ACCESS_TOKEN_ARIAPITA=your_actual_access_token
   
   # Odoo Configuration
   ODOO_API_URL_ARIAPITA=https://your-odoo-instance.com
   ODOO_DATABASE_ARIAPITA=your_database_name
   # ... etc for other locations
   ```

### 4. Kubernetes Deployment

1. **Create Namespace**
   ```bash
   kubectl create namespace omgsushi-pos
   ```

2. **Create Secrets**
   ```bash
   kubectl create secret generic omgsushi-pos-secrets \
     --from-env-file=.env \
     --namespace=omgsushi-pos
   ```

3. **Deploy POS Integration Service**
   ```bash
   kubectl apply -f k8s/pos-integration-service.yaml \
     --namespace=omgsushi-pos
   ```

4. **Deploy Menu Sync Service**
   ```bash
   kubectl apply -f k8s/menu-sync-service.yaml \
     --namespace=omgsushi-pos
   ```

### 5. Webhook Configuration

#### Loyverse Webhooks
1. In Loyverse Back Office → Settings → Webhooks
2. Add webhook URL: `https://api.omgsushi.ttmenus.com/webhooks/loyverse`
3. Select events: Orders, Payments
4. Use the webhook secret from your environment variables

#### Odoo Webhooks
1. Configure Odoo webhooks to point to your API endpoint
2. Ensure proper authentication is set up

## Configuration Details

### Location-Specific Configuration

Each location in `data/locations.yaml` includes:

```yaml
pos:
  loyverse:
    enabled: true
    provider: "loyverse"
    store_id: "{{ env `LOYVERSE_STORE_ID_ARIAPITA` }}"
    access_token: "{{ env `LOYVERSE_ACCESS_TOKEN_ARIAPITA` }}"
    # ... other config
  odoo:
    enabled: true
    provider: "odoo"
    company_id: "{{ env `ODOO_COMPANY_ID_ARIAPITA` }}"
    # ... other config
```

### Menu Synchronization

The system automatically syncs menu items from your Hugo site to POS systems:

1. **Hugo Menu Structure**: Your menu items in `content/` are automatically converted to POS format
2. **POS Mapping**: Use `data/pos-mapping.yaml` to map Hugo menu items to POS products
3. **Automatic Sync**: Menu changes are automatically synchronized with POS systems

### Order Processing Flow

1. **Customer Places Order**: Via your Hugo-based menu
2. **Dual Processing**: Order is sent to both WhatsApp and POS systems
3. **POS Integration**: Order appears in your POS system for processing
4. **Fallback**: If POS is unavailable, WhatsApp ordering continues to work
5. **Status Updates**: Real-time status updates via webhooks

## Troubleshooting

### Common Issues

1. **Orders Not Appearing in POS**
   - Check webhook configuration
   - Verify access tokens are valid
   - Check API endpoint connectivity

2. **Menu Sync Issues**
   - Verify POS system API access
   - Check menu mapping configuration
   - Review sync service logs

3. **Webhook Failures**
   - Verify webhook URLs are accessible
   - Check webhook secret configuration
   - Review webhook service logs

### Logging and Monitoring

- Check pod logs: `kubectl logs -f deployment/pos-integration-service -n omgsushi-pos`
- Monitor webhook deliveries in Loyverse/Odoo admin panels
- Review API endpoint logs for integration issues

## Security Considerations

- **Access Tokens**: Store securely in Kubernetes secrets
- **Webhook Secrets**: Use strong, unique secrets for each POS system
- **API Endpoints**: Secure with proper authentication and HTTPS
- **Network Security**: Use proper ingress controllers and network policies

## Scaling

The system is designed to scale with your business:

- **Multiple Locations**: Easily add new locations by updating configuration
- **Multiple POS Systems**: Support for multiple POS providers per location
- **High Availability**: Kubernetes deployment ensures high availability
- **Load Balancing**: Automatic load balancing across multiple pods

## Support

For technical support or questions:
- Check the troubleshooting section above
- Review service logs for detailed error information
- Contact your system administrator for POS-specific issues

## Advanced Configuration

### Custom POS Providers

To add support for additional POS systems:

1. Implement the POS provider interface in the integration service
2. Add configuration options to `locations.yaml`
3. Update environment variable templates
4. Add provider-specific documentation

### Custom Menu Mapping

For complex menu structures:

1. Use `data/pos-mapping.yaml` for detailed item mapping
2. Implement custom mapping logic in the sync service
3. Add validation for mapped items

### Performance Optimization

- Use connection pooling for POS API calls
- Implement caching for frequently accessed data
- Monitor and optimize database queries
- Use async processing for non-critical operations
