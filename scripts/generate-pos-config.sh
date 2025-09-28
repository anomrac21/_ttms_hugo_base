#!/bin/bash

# POS Configuration Generator for OMG Sushi
# This script helps generate POS configuration for new locations

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to validate location ID
validate_location_id() {
    local location_id=$1
    if [[ ! "$location_id" =~ ^[A-Z_]+$ ]]; then
        print_error "Location ID must be uppercase letters and underscores only"
        return 1
    fi
    return 0
}

# Function to generate environment variables for a location
generate_env_vars() {
    local location_id=$1
    local location_name=$2
    
    print_status "Generating environment variables for location: $location_name ($location_id)"
    
    cat << EOF

# $location_name Location - $location_id
LOYVERSE_STORE_ID_${location_id}=your_${location_id,,}_store_id_here
LOYVERSE_ACCESS_TOKEN_${location_id}=your_${location_id,,}_access_token_here
ODOO_API_URL_${location_id}=https://${location_id,,}-odoo.yourdomain.com
ODOO_DATABASE_${location_id}=omgsushi_${location_id,,}
ODOO_COMPANY_ID_${location_id}=1
ODOO_PARTNER_ID_${location_id}=1
ODOO_POS_CONFIG_ID_${location_id}=1
ODOO_USER_ID_${location_id}=1

EOF
}

# Function to generate locations.yaml entry
generate_location_yaml() {
    local location_id=$1
    local location_name=$2
    local address=$3
    local city=$4
    local lat=$5
    local lon=$6
    local phone=$7
    local whatsapp=$8
    local subcategories=$9
    
    print_status "Generating locations.yaml entry for: $location_name"
    
    cat << EOF
  - address: "$address"
    city: "$city"
    island: "Trinidad"
    subcategories: 
      - $subcategories
    latlon: [$lat,$lon]
    phone: $phone
    whatsapp: $whatsapp
    orderingtables: ["Table 1", "Table 2", "Table 3", "Takeaway Only"]
    delivery:
      fooddrop: https://fooddropcaribbean.com/en/store/OMGSushi/your-store-id
    pos:
      loyverse:
        enabled: true
        provider: "loyverse"
        store_id: "{{ env \`LOYVERSE_STORE_ID_${location_id}\` }}"
        access_token: "{{ env \`LOYVERSE_ACCESS_TOKEN_${location_id}\` }}"
        webhook_secret: "{{ env \`LOYVERSE_WEBHOOK_SECRET\` }}"
        api_url: "{{ env \`POS_API_URL\` }}"
        sync_menu: true
        auto_process_orders: true
        fallback_to_whatsapp: true
      odoo:
        enabled: true
        provider: "odoo"
        company_id: "{{ env \`ODOO_COMPANY_ID_${location_id}\` }}"
        partner_id: "{{ env \`ODOO_PARTNER_ID_${location_id}\` }}"
        pos_config_id: "{{ env \`ODOO_POS_CONFIG_ID_${location_id}\` }}"
        user_id: "{{ env \`ODOO_USER_ID_${location_id}\` }}"
        api_url: "{{ env \`ODOO_API_URL_${location_id}\` }}"
        database: "{{ env \`ODOO_DATABASE_${location_id}\` }}"
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
      tue:
        - type: Open
          time: "11:00"
        - type: Close
          time: "22:00"
      wed:
        - type: Open
          time: "11:00"
        - type: Close
          time: "22:00"
      thu:
        - type: Open
          time: "11:00"
        - type: Close
          time: "22:00"
      fri:
        - type: Open
          time: "11:00"
        - type: Close
          time: "23:00"
      sat:
        - type: Open
          time: "11:00"
        - type: Close
          time: "23:00"

EOF
}

# Function to create POS mapping template
generate_pos_mapping() {
    local location_id=$1
    
    print_status "Generating POS mapping template for: $location_id"
    
    cat << EOF
# POS Mapping for $location_id
# Map Hugo menu items to POS system items

mappings:
  loyverse:
    # Example mapping - customize based on your menu
    # hugo_item_id: pos_item_id
    # "sushi-roll-california": "california-roll-001"
    # "sushi-roll-spicy-tuna": "spicy-tuna-roll-002"
    
  odoo:
    # Example mapping for Odoo
    # hugo_item_id: pos_product_id
    # "sushi-roll-california": 123
    # "sushi-roll-spicy-tuna": 124

# Category mappings
categories:
  loyverse:
    # "hugo-category": "loyverse-category-id"
    
  odoo:
    # "hugo-category": "odoo-category-id"

EOF
}

# Main script
main() {
    print_status "OMG Sushi POS Configuration Generator"
    print_status "====================================="
    
    # Check if running interactively
    if [[ $# -eq 0 ]]; then
        echo "This script helps you generate POS configuration for new OMG Sushi locations."
        echo ""
        echo "Usage: $0 <location_id> <location_name> <address> <city> <lat> <lon> <phone> <whatsapp> <subcategories>"
        echo ""
        echo "Example:"
        echo "  $0 SAN_FERNANDO \"San Fernando\" \"High Street, San Fernando\" \"San Fernando\" 10.2833 -61.4667 18681234567 18681234567 \"Restaurant\""
        echo ""
        echo "Location ID should be uppercase letters and underscores only (e.g., SAN_FERNANDO, CHAGUANAS_CENTRAL)"
        exit 1
    fi
    
    # Validate arguments
    if [[ $# -ne 9 ]]; then
        print_error "Invalid number of arguments. Expected 9 arguments."
        echo "Usage: $0 <location_id> <location_name> <address> <city> <lat> <lon> <phone> <whatsapp> <subcategories>"
        exit 1
    fi
    
    local location_id=$1
    local location_name=$2
    local address=$3
    local city=$4
    local lat=$5
    local lon=$6
    local phone=$7
    local whatsapp=$8
    local subcategories=$9
    
    # Validate location ID
    if ! validate_location_id "$location_id"; then
        exit 1
    fi
    
    print_success "Configuration generation started for: $location_name"
    
    # Generate environment variables
    echo ""
    print_status "Environment Variables (add to your .env file):"
    echo "=================================================="
    generate_env_vars "$location_id" "$location_name"
    
    # Generate locations.yaml entry
    echo ""
    print_status "Locations.yaml Entry (add to data/locations.yaml):"
    echo "========================================================"
    generate_location_yaml "$location_id" "$location_name" "$address" "$city" "$lat" "$lon" "$phone" "$whatsapp" "$subcategories"
    
    # Generate POS mapping template
    local mapping_file="data/pos-mapping-${location_id,,}.yaml"
    print_status "Creating POS mapping template: $mapping_file"
    generate_pos_mapping "$location_id" > "$mapping_file"
    
    print_success "Configuration generation completed!"
    print_warning "Don't forget to:"
    echo "  1. Add the environment variables to your .env file"
    echo "  2. Add the location entry to data/locations.yaml"
    echo "  3. Configure your POS systems with the new location"
    echo "  4. Update your Kubernetes secrets"
    echo "  5. Customize the POS mapping in $mapping_file"
}

# Run main function with all arguments
main "$@"
