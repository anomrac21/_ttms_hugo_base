#!/usr/bin/env python3
"""
Menu Conversion Script for OMG Sushi Hugo Site
Converts Hugo menu structure to POS-compatible format
"""

import os
import yaml
import json
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MenuConverter:
    """Converts Hugo menu structure to POS-compatible format"""
    
    def __init__(self, content_dir: str = "content", data_dir: str = "data"):
        self.content_dir = Path(content_dir)
        self.data_dir = Path(data_dir)
        self.menu_data = {}
        self.pos_mapping = {}
        
    def load_pos_mapping(self) -> None:
        """Load POS mapping configuration"""
        mapping_file = self.data_dir / "pos-mapping.yaml"
        if mapping_file.exists():
            with open(mapping_file, 'r', encoding='utf-8') as f:
                self.pos_mapping = yaml.safe_load(f) or {}
            logger.info(f"Loaded POS mapping from {mapping_file}")
        else:
            logger.warning(f"POS mapping file not found: {mapping_file}")
    
    def load_menu_data(self) -> None:
        """Load existing menu data from data directory"""
        menu_file = self.data_dir / "menudata.yaml"
        if menu_file.exists():
            with open(menu_file, 'r', encoding='utf-8') as f:
                self.menu_data = yaml.safe_load(f) or {}
            logger.info(f"Loaded existing menu data from {menu_file}")
    
    def scan_menu_items(self) -> Dict[str, Any]:
        """Scan Hugo content directory for menu items"""
        menu_items = {}
        
        # Walk through content directory
        for content_file in self.content_dir.rglob("*.md"):
            if content_file.name.startswith('_index.md'):
                continue
                
            try:
                with open(content_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Parse front matter and content
                item_data = self.parse_menu_item(content_file, content)
                if item_data:
                    menu_items[item_data['slug']] = item_data
                    
            except Exception as e:
                logger.error(f"Error processing {content_file}: {e}")
        
        logger.info(f"Found {len(menu_items)} menu items")
        return menu_items
    
    def parse_menu_item(self, file_path: Path, content: str) -> Optional[Dict[str, Any]]:
        """Parse a single menu item from Hugo markdown file"""
        lines = content.split('\n')
        
        if not lines or not lines[0].startswith('---'):
            return None
        
        # Extract front matter
        front_matter = []
        content_start = 0
        in_front_matter = False
        
        for i, line in enumerate(lines):
            if line.startswith('---'):
                if not in_front_matter:
                    in_front_matter = True
                else:
                    content_start = i + 1
                    break
            elif in_front_matter:
                front_matter.append(line)
        
        if not front_matter:
            return None
        
        try:
            # Parse YAML front matter
            front_matter_yaml = '\n'.join(front_matter)
            item_data = yaml.safe_load(front_matter_yaml) or {}
            
            # Add computed fields
            item_data['slug'] = file_path.stem
            item_data['file_path'] = str(file_path)
            item_data['category'] = self.extract_category(file_path)
            
            # Extract content
            content_lines = lines[content_start:]
            item_data['content'] = '\n'.join(content_lines).strip()
            
            # Validate required fields
            if not self.validate_menu_item(item_data):
                return None
            
            return item_data
            
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML in {file_path}: {e}")
            return None
    
    def extract_category(self, file_path: Path) -> str:
        """Extract category from file path"""
        # Remove content_dir from path and get parent directory
        relative_path = file_path.relative_to(self.content_dir)
        if len(relative_path.parts) > 1:
            return relative_path.parts[0]
        return "uncategorized"
    
    def validate_menu_item(self, item_data: Dict[str, Any]) -> bool:
        """Validate menu item has required fields"""
        required_fields = ['title', 'price']
        
        for field in required_fields:
            if field not in item_data or not item_data[field]:
                logger.warning(f"Menu item missing required field '{field}': {item_data.get('slug', 'unknown')}")
                return False
        
        # Validate price format
        try:
            price = float(str(item_data['price']).replace('$', '').replace(',', ''))
            item_data['price_numeric'] = price
        except (ValueError, TypeError):
            logger.warning(f"Invalid price format for item {item_data.get('slug', 'unknown')}: {item_data.get('price')}")
            return False
        
        return True
    
    def convert_to_pos_format(self, menu_items: Dict[str, Any]) -> Dict[str, Any]:
        """Convert menu items to POS-compatible format"""
        pos_items = {
            'loyverse': {},
            'odoo': {}
        }
        
        for slug, item_data in menu_items.items():
            # Apply global mappings
            global_mappings = self.pos_mapping.get('global', {})
            
            # Loyverse mapping
            loyverse_global = global_mappings.get('loyverse', {}).get('items', {})
            loyverse_id = loyverse_global.get(slug, f"omg-sushi-{slug}")
            
            pos_items['loyverse'][loyverse_id] = {
                'name': item_data['title'],
                'price': item_data['price_numeric'],
                'description': item_data.get('description', ''),
                'category': item_data['category'],
                'available': item_data.get('available', True),
                'sku': loyverse_id,
                'hugo_slug': slug
            }
            
            # Odoo mapping
            odoo_global = global_mappings.get('odoo', {}).get('items', {})
            odoo_id = odoo_global.get(slug, f"omg-sushi-{slug}")
            
            pos_items['odoo'][odoo_id] = {
                'name': item_data['title'],
                'list_price': item_data['price_numeric'],
                'description': item_data.get('description', ''),
                'categ_id': item_data['category'],
                'active': item_data.get('available', True),
                'default_code': odoo_id,
                'hugo_slug': slug
            }
        
        return pos_items
    
    def save_pos_data(self, pos_items: Dict[str, Any]) -> None:
        """Save POS-formatted data to files"""
        # Save as YAML
        pos_file = self.data_dir / "pos-menu-data.yaml"
        with open(pos_file, 'w', encoding='utf-8') as f:
            yaml.dump(pos_items, f, default_flow_style=False, allow_unicode=True)
        logger.info(f"Saved POS menu data to {pos_file}")
        
        # Save as JSON
        json_file = self.data_dir / "pos-menu-data.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(pos_items, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved POS menu data to {json_file}")
        
        # Save individual POS system files
        for pos_system, items in pos_items.items():
            system_file = self.data_dir / f"pos-menu-{pos_system}.yaml"
            with open(system_file, 'w', encoding='utf-8') as f:
                yaml.dump(items, f, default_flow_style=False, allow_unicode=True)
            logger.info(f"Saved {pos_system} menu data to {system_file}")
    
    def generate_mapping_report(self, menu_items: Dict[str, Any]) -> None:
        """Generate a mapping report showing which items need POS mapping"""
        report_file = self.data_dir / "mapping-report.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# Menu Item Mapping Report\n\n")
            f.write(f"Generated on: {Path().cwd()}\n\n")
            f.write(f"Total menu items found: {len(menu_items)}\n\n")
            
            f.write("## Items Requiring POS Mapping\n\n")
            
            global_mappings = self.pos_mapping.get('global', {})
            loyverse_mappings = global_mappings.get('loyverse', {}).get('items', {})
            odoo_mappings = global_mappings.get('odoo', {}).get('items', {})
            
            f.write("| Hugo Slug | Title | Category | Price | Loyverse Mapped | Odoo Mapped |\n")
            f.write("|-----------|-------|----------|-------|-----------------|-------------|\n")
            
            for slug, item_data in menu_items.items():
                loyverse_mapped = "✅" if slug in loyverse_mappings else "❌"
                odoo_mapped = "✅" if slug in odoo_mappings else "❌"
                
                f.write(f"| {slug} | {item_data['title']} | {item_data['category']} | ${item_data['price_numeric']:.2f} | {loyverse_mapped} | {odoo_mapped} |\n")
            
            f.write("\n## Mapping Instructions\n\n")
            f.write("1. Edit `data/pos-mapping.yaml` to add mappings for unmapped items\n")
            f.write("2. Use the format: `\"hugo-slug\": \"pos-item-id\"`\n")
            f.write("3. Run this script again to regenerate POS data\n")
        
        logger.info(f"Generated mapping report: {report_file}")
    
    def run_conversion(self) -> None:
        """Run the complete menu conversion process"""
        logger.info("Starting menu conversion process...")
        
        # Load configurations
        self.load_pos_mapping()
        self.load_menu_data()
        
        # Scan for menu items
        menu_items = self.scan_menu_items()
        if not menu_items:
            logger.warning("No menu items found")
            return
        
        # Convert to POS format
        pos_items = self.convert_to_pos_format(menu_items)
        
        # Save results
        self.save_pos_data(pos_items)
        
        # Generate mapping report
        self.generate_mapping_report(menu_items)
        
        logger.info("Menu conversion completed successfully!")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Convert Hugo menu to POS format')
    parser.add_argument('--content-dir', default='content', help='Hugo content directory')
    parser.add_argument('--data-dir', default='data', help='Hugo data directory')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    converter = MenuConverter(args.content_dir, args.data_dir)
    converter.run_conversion()


if __name__ == '__main__':
    main()
