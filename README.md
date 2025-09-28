# OMG Sushi Hugo Template

A modern, scalable Hugo template for restaurant menu websites with integrated POS system support.

## Features

- 🍣 **Modern Restaurant Menu**: Beautiful, responsive menu display
- 📱 **Mobile-First Design**: Optimized for mobile ordering
- 🏪 **Multi-Location Support**: Handle multiple restaurant locations
- 💳 **POS Integration**: Support for Loyverse, Odoo, and other POS systems
- 📞 **WhatsApp Ordering**: Integrated WhatsApp ordering system
- 🔄 **Menu Synchronization**: Automatic menu sync with POS systems
- 🌐 **Multi-Language Support**: Built-in internationalization
- ⚡ **Fast Performance**: Optimized for speed and SEO
- 🔧 **Easy Configuration**: Simple YAML-based configuration

## Quick Start

### Prerequisites

- Hugo Extended (v0.140.2 or later)
- Git
- Python 3.8+ (for menu conversion scripts)

### Installation

1. **Clone the template**
   ```bash
   git clone <your-repo-url> my-restaurant-menu
   cd my-restaurant-menu
   ```

2. **Initialize and update submodules**
   ```bash
   bash ./build.sh
   ```

3. **Configure your restaurant**
   - Edit `hugo.toml` with your restaurant details
   - Update `data/locations.yaml` with your locations
   - Customize `static/branding/` with your logos and images

4. **Set up POS integration (optional)**
   ```bash
   cp env.example .env
   # Edit .env with your POS system credentials
   ```

5. **Build and serve**
   ```bash
   hugo server
   ```

## Configuration

### Basic Configuration

Edit `hugo.toml` to customize your restaurant:

```toml
baseURL = 'https://your-restaurant.ttmenus.com/'
title = 'Your Restaurant Name'

[params.services]
  onesignalid = "your-onesignal-id"
  analyticsid = 1
  notifications = true

[params.orderingsystem]
  vat = 0
  servicecharge = 0
  hastables = true
  whatsapp = 18681234567

[params.social]
  facebook = "https://facebook.com/yourrestaurant"
  instagram = "https://instagram.com/yourrestaurant"
  phone = 18681234567
```

### Location Configuration

Configure your restaurant locations in `data/locations.yaml`:

```yaml
locations:
  - address: "123 Main Street, City"
    city: "City Name"
    island: "Trinidad"
    subcategories: ["Restaurant", "Bar"]
    latlon: [10.659223458630825, -61.51971280000002]
    phone: 18681234567
    whatsapp: 18681234567
    orderingtables: ["Table 1", "Table 2", "Takeaway Only"]
    pos:
      loyverse:
        enabled: true
        provider: "loyverse"
        store_id: "{{ env `LOYVERSE_STORE_ID` }}"
        # ... other configuration
```

## POS Integration

### Supported POS Systems

- **Loyverse**: Cloud-based POS system
- **Odoo**: Enterprise POS system
- **Custom APIs**: Extensible for other POS systems

### Setup POS Integration

1. **Configure environment variables**
   ```bash
   # Copy and edit environment template
   cp env.example .env
   
   # Add your POS system credentials
   LOYVERSE_ACCESS_TOKEN=your_token_here
   LOYVERSE_STORE_ID=your_store_id_here
   ```

2. **Map menu items**
   Edit `data/pos-mapping.yaml` to map your Hugo menu items to POS system items:
   ```yaml
   global:
     loyverse:
       items:
         "sushi-roll-california": "california-roll-001"
         "sashimi-salmon": "salmon-sashimi-002"
   ```

3. **Convert menu for POS**
   ```bash
   python convert_menu.py
   ```

### Adding New Locations

Use the configuration generator script:

```bash
./scripts/generate-pos-config.sh SAN_FERNANDO "San Fernando" "High Street, San Fernando" "San Fernando" 10.2833 -61.4667 18681234567 18681234567 "Restaurant"
```

## Menu Management

### Adding Menu Items

1. **Create menu categories**
   ```bash
   mkdir -p content/your-category
   echo "---\ntitle: Your Category\n---" > content/your-category/_index.md
   ```

2. **Add menu items**
   Create markdown files in category directories:
   ```markdown
   ---
   title: "California Roll"
   price: "$15.99"
   description: "Fresh avocado, cucumber, and crab"
   image: "/images/california-roll.jpg"
   allergens: ["Crab", "Sesame"]
   ---
   
   Delicious California roll with fresh ingredients.
   ```

3. **Convert to POS format**
   ```bash
   python convert_menu.py
   ```

### Menu Structure

```
content/
├── _index.md                 # Homepage
├── appetizers/
│   ├── _index.md            # Category page
│   ├── edamame.md          # Menu item
│   └── miso-soup.md        # Menu item
├── sushi-rolls/
│   ├── _index.md
│   ├── california-roll.md
│   └── spicy-tuna-roll.md
└── beverages/
    ├── _index.md
    ├── green-tea.md
    └── sake.md
```

## Deployment

### Netlify (Recommended)

1. **Connect your repository** to Netlify
2. **Set build settings**:
   - Build command: `bash ./build.sh`
   - Publish directory: `public`
   - Hugo version: `0.140.2`

3. **Add environment variables** in Netlify dashboard:
   - Copy variables from your `.env` file
   - Add `GIT_SUBMODULE_STRATEGY=recursive`

### Manual Deployment

1. **Build the site**
   ```bash
   bash ./build.sh
   ```

2. **Deploy public directory** to your web server

### Kubernetes Deployment

For advanced deployments with POS integration:

1. **Create Kubernetes secrets**
   ```bash
   kubectl create secret generic restaurant-pos-secrets \
     --from-env-file=.env \
     --namespace=restaurant-pos
   ```

2. **Deploy POS integration services**
   ```bash
   kubectl apply -f k8s/ -n restaurant-pos
   ```

## Customization

### Branding

Replace files in `static/branding/`:
- `favicon.ico` - Website favicon
- `logo.png` - Restaurant logo
- `hero-bg.jpg` - Hero background image

### Styling

Customize CSS in `static/css/`:
- `custom.css` - Custom styles
- `colors.css` - Color scheme

### JavaScript

Add custom functionality in `static/js/`:
- `custom.js` - Custom JavaScript
- `ordersystem.js` - Order system modifications

## Scripts

### Menu Conversion
```bash
python convert_menu.py [--content-dir content] [--data-dir data]
```

### POS Configuration Generator
```bash
./scripts/generate-pos-config.sh LOCATION_ID "Location Name" "Address" "City" LAT LON PHONE WHATSAPP "Subcategories"
```

### Build Script
```bash
bash ./build.sh
```

## Documentation

- [POS Integration Guide](POS_INTEGRATION_GUIDE.md) - Complete POS setup guide
- [Scalable POS Configuration](SCALABLE_POS_CONFIGURATION.md) - Multi-location setup
- [Menu Conversion Script](convert_menu.py) - Menu format conversion

## Support

For support and questions:
1. Check the documentation files
2. Review the troubleshooting sections
3. Check GitHub issues
4. Contact your system administrator

## License

This template is licensed under the MIT License. See LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Changelog

### Version 2.0.0
- Added POS integration support
- Multi-location configuration
- Enhanced menu conversion tools
- Improved documentation
- Modern Hugo configuration
- Scalable architecture

### Version 1.0.0
- Initial release
- Basic Hugo template
- WhatsApp ordering
- Mobile-responsive design
