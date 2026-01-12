"""
Script to import historical data from various sources into Argus.
Supports CSV, JSON, and structured data formats.
"""

import csv
import json
import argparse
from datetime import datetime
from typing import Dict, List, Any
import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.history_engine import HistoryEngine
from src.data.history_models import (
    HistoricalEvent, HistoricalFigure, HistoricalOrganization,
    HistoricalPeriod, Timeline, EventType, PeriodType
)


class HistoryDataImporter:
    """Import historical data from various sources"""
    
    def __init__(self):
        self.engine = HistoryEngine()
    
    def import_from_csv(self, file_path: str, data_type: str) -> int:
        """Import data from CSV file"""
        count = 0
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                for row in reader:
                    if data_type == "events":
                        self._import_event_from_row(row)
                    elif data_type == "figures":
                        self._import_figure_from_row(row)
                    elif data_type == "organizations":
                        self._import_organization_from_row(row)
                    elif data_type == "periods":
                        self._import_period_from_row(row)
                    
                    count += 1
        
        except Exception as e:
            print(f"Error importing CSV: {e}")
            return 0
        
        return count
    
    def import_from_json(self, file_path: str) -> int:
        """Import data from JSON file"""
        count = 0
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            if isinstance(data, list):
                for item in data:
                    self._import_item_from_dict(item)
                    count += 1
            elif isinstance(data, dict):
                for item_type, items in data.items():
                    if isinstance(items, list):
                        for item in items:
                            self._import_item_from_dict(item, item_type)
                            count += 1
        
        except Exception as e:
            print(f"Error importing JSON: {e}")
            return 0
        
        return count
    
    def import_sample_data(self) -> int:
        """Import sample historical data for demonstration"""
        count = 0
        
        # Sample periods
        periods = [
            {
                "name": "Ancient Egypt",
                "description": "Period of ancient Egyptian civilization",
                "start_date": "-3100-01-01",
                "end_date": "0030-01-01",
                "period_type": "ancient",
                "region": "North Africa",
                "key_characteristics": ["Pyramid building", "Hieroglyphic writing", "Pharaonic rule"]
            },
            {
                "name": "Classical Greece",
                "description": "Period of ancient Greek civilization",
                "start_date": "-0800-01-01",
                "end_date": "-0146-01-01",
                "period_type": "classical",
                "region": "Southern Europe",
                "key_characteristics": ["Democracy", "Philosophy", "Olympic Games", "Theater"]
            },
            {
                "name": "Industrial Revolution",
                "description": "Period of rapid industrialization",
                "start_date": "1760-01-01",
                "end_date": "1840-01-01",
                "period_type": "modern",
                "region": "Europe, North America",
                "key_characteristics": ["Steam power", "Factory system", "Urbanization"]
            }
        ]
        
        for period_data in periods:
            period = self._create_period_from_dict(period_data)
            self.engine.add_period(period)
            count += 1
        
        # Sample figures
        figures = [
            {
                "name": "Cleopatra VII",
                "birth_date": "-0069-01-01",
                "death_date": "-0030-01-01",
                "birth_place": "Alexandria, Egypt",
                "death_place": "Alexandria, Egypt",
                "occupation": ["Pharaoh", "Queen"],
                "achievements": ["Last ruler of Ptolemaic Egypt", "Alliance with Rome"],
                "era": "Ancient Egypt",
                "biography": "Cleopatra VII Philopator was the last active ruler of the Ptolemaic Kingdom of Egypt."
            },
            {
                "name": "Socrates",
                "birth_date": "-0470-01-01",
                "death_date": "-0399-01-01",
                "birth_place": "Athens, Greece",
                "death_place": "Athens, Greece",
                "occupation": ["Philosopher"],
                "achievements": ["Socratic method", "Foundation of Western philosophy"],
                "era": "Classical Greece",
                "biography": "Socrates was a classical Greek philosopher credited as one of the founders of Western philosophy."
            },
            {
                "name": "James Watt",
                "birth_date": "1736-01-19",
                "death_date": "1819-08-25",
                "birth_place": "Greenock, Scotland",
                "death_place": "Birmingham, England",
                "occupation": ["Inventor", "Engineer"],
                "achievements": ["Improved steam engine", "Horsepower unit"],
                "era": "Industrial Revolution",
                "biography": "James Watt was a Scottish inventor, mechanical engineer, and chemist who improved the Newcomen steam engine."
            }
        ]
        
        for figure_data in figures:
            figure = self._create_figure_from_dict(figure_data)
            self.engine.add_figure(figure)
            count += 1
        
        # Sample events
        events = [
            {
                "title": "Battle of Actium",
                "description": "Final war of the Roman Republic",
                "event_type": "military",
                "date": "-0031-09-02",
                "location": "Ionian Sea, near Actium",
                "significance": "Marked the end of the Roman Republic and beginning of Roman Empire",
                "tags": ["roman", "civil war", "egypt"]
            },
            {
                "title": "Peloponnesian War",
                "description": "Ancient Greek war between Athens and Sparta",
                "event_type": "military",
                "date": "-0431-01-01",
                "end_date": "-0404-01-01",
                "location": "Greece",
                "significance": "Reshaped the Greek world and ended the golden age of Athens",
                "tags": ["greece", "war", "athens", "sparta"]
            },
            {
                "title": "First Steam Engine Patent",
                "description": "James Watt received patent for improved steam engine",
                "event_type": "technological",
                "date": "1769-01-05",
                "location": "London, England",
                "significance": "Key development in the Industrial Revolution",
                "tags": ["industrial revolution", "technology", "steam power"]
            }
        ]
        
        for event_data in events:
            event = self._create_event_from_dict(event_data)
            self.engine.add_event(event)
            count += 1
        
        return count
    
    def _import_event_from_row(self, row: Dict[str, str]):
        """Import event from CSV row"""
        try:
            event = HistoricalEvent(
                title=row.get('title', ''),
                description=row.get('description', ''),
                event_type=EventType(row.get('event_type', 'political')),
                date=datetime.fromisoformat(row.get('date', '')).date(),
                end_date=datetime.fromisoformat(row['end_date']).date() if row.get('end_date') else None,
                location=row.get('location', ''),
                coordinates=self._parse_coordinates(row.get('coordinates')),
                participants=self._parse_list(row.get('participants', '')),
                causes=self._parse_list(row.get('causes', '')),
                consequences=self._parse_list(row.get('consequences', '')),
                sources=self._parse_list(row.get('sources', '')),
                significance=row.get('significance', ''),
                tags=self._parse_list(row.get('tags', ''))
            )
            self.engine.add_event(event)
        except Exception as e:
            print(f"Error importing event row: {e}")
    
    def _import_figure_from_row(self, row: Dict[str, str]):
        """Import figure from CSV row"""
        try:
            figure = HistoricalFigure(
                name=row.get('name', ''),
                birth_date=datetime.fromisoformat(row['birth_date']).date() if row.get('birth_date') else None,
                death_date=datetime.fromisoformat(row['death_date']).date() if row.get('death_date') else None,
                birth_place=row.get('birth_place'),
                death_place=row.get('death_place'),
                occupation=self._parse_list(row.get('occupation', '')),
                achievements=self._parse_list(row.get('achievements', '')),
                relationships=self._parse_dict(row.get('relationships', '')),
                affiliations=self._parse_list(row.get('affiliations', '')),
                era=row.get('era', ''),
                biography=row.get('biography', ''),
                portrait_url=row.get('portrait_url')
            )
            self.engine.add_figure(figure)
        except Exception as e:
            print(f"Error importing figure row: {e}")
    
    def _import_organization_from_row(self, row: Dict[str, str]):
        """Import organization from CSV row"""
        try:
            org = HistoricalOrganization(
                name=row.get('name', ''),
                organization_type=row.get('organization_type', ''),
                founded_date=datetime.fromisoformat(row['founded_date']).date() if row.get('founded_date') else None,
                dissolved_date=datetime.fromisoformat(row['dissolved_date']).date() if row.get('dissolved_date') else None,
                headquarters=row.get('headquarters'),
                territory=self._parse_list(row.get('territory', '')),
                leaders=self._parse_list(row.get('leaders', '')),
                achievements=self._parse_list(row.get('achievements', '')),
                conflicts=self._parse_list(row.get('conflicts', ''))
            )
            self.engine.add_organization(org)
        except Exception as e:
            print(f"Error importing organization row: {e}")
    
    def _import_period_from_row(self, row: Dict[str, str]):
        """Import period from CSV row"""
        try:
            period = HistoricalPeriod(
                name=row.get('name', ''),
                description=row.get('description', ''),
                start_date=datetime.fromisoformat(row['start_date']).date(),
                end_date=datetime.fromisoformat(row['end_date']).date() if row.get('end_date') else None,
                period_type=PeriodType(row.get('period_type', 'modern')),
                region=row.get('region', ''),
                key_characteristics=self._parse_list(row.get('key_characteristics', '')),
                related_periods=self._parse_list(row.get('related_periods', ''))
            )
            self.engine.add_period(period)
        except Exception as e:
            print(f"Error importing period row: {e}")
    
    def _import_item_from_dict(self, item: Dict[str, Any], item_type: str = None):
        """Import item from dictionary"""
        try:
            if item_type:
                item_type = item_type.lower()
            else:
                # Try to infer type from the data
                if 'title' in item and 'event_type' in item:
                    item_type = 'events'
                elif 'name' in item and 'era' in item:
                    item_type = 'figures'
                elif 'name' in item and 'organization_type' in item:
                    item_type = 'organizations'
                elif 'name' in item and 'period_type' in item:
                    item_type = 'periods'
                else:
                    item_type = 'unknown'
            
            if item_type == 'events':
                event = self._create_event_from_dict(item)
                self.engine.add_event(event)
            elif item_type == 'figures':
                figure = self._create_figure_from_dict(item)
                self.engine.add_figure(figure)
            elif item_type == 'organizations':
                org = self._create_organization_from_dict(item)
                self.engine.add_organization(org)
            elif item_type == 'periods':
                period = self._create_period_from_dict(item)
                self.engine.add_period(period)
        
        except Exception as e:
            print(f"Error importing item: {e}")
    
    def _create_event_from_dict(self, data: Dict[str, Any]) -> HistoricalEvent:
        """Create event from dictionary"""
        return HistoricalEvent(
            title=data.get('title', ''),
            description=data.get('description', ''),
            event_type=EventType(data.get('event_type', 'political')),
            date=datetime.fromisoformat(data['date']).date(),
            end_date=datetime.fromisoformat(data['end_date']).date() if data.get('end_date') else None,
            location=data.get('location', ''),
            coordinates=tuple(data.get('coordinates', [])) if data.get('coordinates') else None,
            participants=data.get('participants', []),
            causes=data.get('causes', []),
            consequences=data.get('consequences', []),
            sources=data.get('sources', []),
            significance=data.get('significance', ''),
            tags=data.get('tags', [])
        )
    
    def _create_figure_from_dict(self, data: Dict[str, Any]) -> HistoricalFigure:
        """Create figure from dictionary"""
        return HistoricalFigure(
            name=data.get('name', ''),
            birth_date=datetime.fromisoformat(data['birth_date']).date() if data.get('birth_date') else None,
            death_date=datetime.fromisoformat(data['death_date']).date() if data.get('death_date') else None,
            birth_place=data.get('birth_place'),
            death_place=data.get('death_place'),
            occupation=data.get('occupation', []),
            achievements=data.get('achievements', []),
            relationships=data.get('relationships', {}),
            affiliations=data.get('affiliations', []),
            era=data.get('era', ''),
            biography=data.get('biography', ''),
            portrait_url=data.get('portrait_url')
        )
    
    def _create_organization_from_dict(self, data: Dict[str, Any]) -> HistoricalOrganization:
        """Create organization from dictionary"""
        return HistoricalOrganization(
            name=data.get('name', ''),
            organization_type=data.get('organization_type', ''),
            founded_date=datetime.fromisoformat(data['founded_date']).date() if data.get('founded_date') else None,
            dissolved_date=datetime.fromisoformat(data['dissolved_date']).date() if data.get('dissolved_date') else None,
            headquarters=data.get('headquarters'),
            territory=data.get('territory', []),
            leaders=data.get('leaders', []),
            achievements=data.get('achievements', []),
            conflicts=data.get('conflicts', [])
        )
    
    def _create_period_from_dict(self, data: Dict[str, Any]) -> HistoricalPeriod:
        """Create period from dictionary"""
        return HistoricalPeriod(
            name=data.get('name', ''),
            description=data.get('description', ''),
            start_date=datetime.fromisoformat(data['start_date']).date(),
            end_date=datetime.fromisoformat(data['end_date']).date() if data.get('end_date') else None,
            period_type=PeriodType(data.get('period_type', 'modern')),
            region=data.get('region', ''),
            key_characteristics=data.get('key_characteristics', []),
            related_periods=data.get('related_periods', [])
        )
    
    def _parse_coordinates(self, coord_str: str) -> List[float]:
        """Parse coordinates from string"""
        if not coord_str:
            return None
        try:
            coords = [float(x.strip()) for x in coord_str.split(',')]
            return coords if len(coords) == 2 else None
        except:
            return None
    
    def _parse_list(self, list_str: str) -> List[str]:
        """Parse list from string"""
        if not list_str:
            return []
        return [item.strip() for item in list_str.split(';') if item.strip()]
    
    def _parse_dict(self, dict_str: str) -> Dict[str, str]:
        """Parse dictionary from string"""
        if not dict_str:
            return {}
        result = {}
        try:
            pairs = [item.strip() for item in dict_str.split(';')]
            for pair in pairs:
                if ':' in pair:
                    key, value = pair.split(':', 1)
                    result[key.strip()] = value.strip()
        except:
            pass
        return result


def main():
    """Main function for CLI usage"""
    parser = argparse.ArgumentParser(description='Import historical data into Argus')
    parser.add_argument('command', choices=['csv', 'json', 'sample'], help='Import command')
    parser.add_argument('--file', help='File to import from')
    parser.add_argument('--type', choices=['events', 'figures', 'organizations', 'periods'], 
                       help='Data type for CSV import')
    
    args = parser.parse_args()
    
    importer = HistoryDataImporter()
    
    if args.command == 'csv':
        if not args.file or not args.type:
            print("Error: CSV import requires --file and --type arguments")
            return
        
        count = importer.import_from_csv(args.file, args.type)
        print(f"Imported {count} items from {args.file}")
    
    elif args.command == 'json':
        if not args.file:
            print("Error: JSON import requires --file argument")
            return
        
        count = importer.import_from_json(args.file)
        print(f"Imported {count} items from {args.file}")
    
    elif args.command == 'sample':
        count = importer.import_sample_data()
        print(f"Imported {count} sample items")
    
    # Print statistics
    stats = importer.engine.get_statistics()
    print("\nDatabase Statistics:")
    print(f"Events: {stats['total_events']}")
    print(f"Figures: {stats['total_figures']}")
    print(f"Organizations: {stats['total_organizations']}")
    print(f"Periods: {stats['total_periods']}")


if __name__ == "__main__":
    main()
