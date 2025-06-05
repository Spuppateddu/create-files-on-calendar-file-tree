import os
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class CalendarFileCreator:
    def __init__(self):
        self.file_types = {
            'work': self._can_create_work_file,
            'note': self._can_create_note_file,
            'workout': self._can_create_workout_file,
            'youtube': self._can_create_youtube_file,
            'news': self._can_create_news_file
        }
        self.delete_empty_flags = {
            'work': 'CAN_DELETE_EMPTY_PAST_WORK_FILES',
            'note': 'CAN_DELETE_EMPTY_PAST_NOTE_FILES',
            'workout': 'CAN_DELETE_EMPTY_PAST_WORKOUT_FILES',
            'youtube': 'CAN_DELETE_EMPTY_PAST_YOUTUBE_FILES',
            'news': 'CAN_DELETE_EMPTY_PAST_NEWS_FILES'
        }
        # Get base path from environment or use default
        self.base_path = Path(os.getenv('CALENDAR_BASE_PATH', 'calendar'))
        # Create base directory if it doesn't exist
        self.base_path.mkdir(exist_ok=True)

    def _find_latest_year(self):
        """Find the latest year in the calendar structure."""
        latest_year = datetime.now().year
        if self.base_path.exists():
            years = [int(x.name) for x in self.base_path.iterdir() 
                    if x.is_dir() and x.name.isdigit()]
            if years:
                latest_year = max(years)
        return latest_year

    def _can_create_past_files(self):
        return os.getenv('CAN_CREATE_PAST_FILES', 'false').lower() == 'true'

    def _can_create_work_file(self, is_future):
        if is_future:
            return os.getenv('CAN_CREATE_FUTURE_WORK_FILES', 'false').lower() == 'true'
        return os.getenv('CAN_CREATE_WORK_FILES', 'false').lower() == 'true'

    def _can_create_note_file(self, is_future):
        if is_future:
            return os.getenv('CAN_CREATE_FUTURE_NOTE_FILES', 'false').lower() == 'true'
        return os.getenv('CAN_CREATE_NOTE_FILES', 'false').lower() == 'true'

    def _can_create_workout_file(self, is_future):
        if is_future:
            return os.getenv('CAN_CREATE_FUTURE_WORKOUT_FILES', 'false').lower() == 'true'
        return os.getenv('CAN_CREATE_WORKOUT_FILES', 'false').lower() == 'true'

    def _can_create_youtube_file(self, is_future):
        if is_future:
            return os.getenv('CAN_CREATE_FUTURE_YOUTUBE_FILES', 'false').lower() == 'true'
        return os.getenv('CAN_CREATE_YOUTUBE_FILES', 'false').lower() == 'true'

    def _can_create_news_file(self, is_future):
        if is_future:
            return os.getenv('CAN_CREATE_FUTURE_NEWS_FILES', 'false').lower() == 'true'
        return os.getenv('CAN_CREATE_NEWS_FILES', 'false').lower() == 'true'

    def _create_folder_structure(self, date):
        year = str(date.year)
        month = f"{date.month:02d}-{date.strftime('%B')}"
        day = f"{date.day:02d}-{date.strftime('%A')}"
        
        # Use base_path for creating the full path
        path = self.base_path / year / month / day
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _is_file_empty(self, file_path, date, file_type):
        """Check if a file is empty or contains only the title."""
        if not file_path.exists():
            return False

        try:
            with open(file_path, 'r') as f:
                content = f.read().strip()
                # Check if file is completely empty
                if not content:
                    print(f"File is completely empty: {file_path}")
                    return True
                
                # Check if file contains only the title
                day_str = f"{date.day} {date.strftime('%A')} {date.strftime('%B')} {date.year}"
                expected_title = f"# {day_str} - {file_type.capitalize()}"
                
                # Also check without the type suffix for backward compatibility
                alternative_title = f"# {day_str}"
                
                is_empty = content == expected_title or content == alternative_title
                if is_empty:
                    print(f"File contains only title: {file_path}")
                return is_empty
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return False

    def _delete_empty_past_file(self, file_path, date, file_type):
        """Delete empty past files if configured to do so."""
        if not file_path.exists():
            return

        # Only delete past files
        if date.date() >= datetime.now().date():
            return

        # Check if deletion is enabled for this file type
        flag_name = self.delete_empty_flags.get(file_type)
        if not flag_name:
            return
            
        flag_value = os.getenv(flag_name, 'false').lower()
        
        if flag_value != 'true':
            return

        # Check if file is empty and delete if it is
        if self._is_file_empty(file_path, date, file_type):
            try:
                file_path.unlink()
            except Exception as e:
                print(f"Error deleting file {file_path}: {e}")

    def _create_file(self, date, file_type):
        # Check if we can create this type of file
        is_future = date.date() > datetime.now().date()
        is_past = date.date() < datetime.now().date()

        if is_past:
            if not self._can_create_past_files():
                return
        elif is_future:
            pass
        else:
            pass

        if not self.file_types[file_type](is_future):
            return

        # Create folder structure
        folder_path = self._create_folder_structure(date)
        
        # Create file name and content
        file_name = f"{file_type}.md"
        file_path = folder_path / file_name

        # Check for empty past files and delete if configured
        self._delete_empty_past_file(file_path, date, file_type)
        
        # Skip if file already exists
        if file_path.exists():
            return

        # Create file content
        day_str = f"{date.day} {date.strftime('%A')} {date.strftime('%B')} {date.year}"
        content = f"# {day_str} - {file_type.capitalize()}"
        
        # Write file
        try:
            with open(file_path, 'w') as f:
                f.write(content)
        except Exception as e:
            print(f"Error creating file {file_path}: {e}")

    def create_files_for_date(self, date):
        for file_type in self.file_types.keys():
            self._create_file(date, file_type)

    def create_files_for_range(self, start_date, end_date):
        current_date = start_date
        while current_date <= end_date:
            self.create_files_for_date(current_date)
            current_date += timedelta(days=1)

    def clean_empty_files(self, start_date=None, end_date=None):
        """Clean empty files in a date range."""
        if start_date is None:
            start_date = datetime(2000, 1, 1)  # Safe default start date
        if end_date is None:
            end_date = datetime(self._find_latest_year(), 12, 31)

        current_date = start_date
        while current_date <= end_date:
            for file_type in self.file_types.keys():
                folder_path = self._create_folder_structure(current_date)
                file_path = folder_path / f"{file_type}.md"
                self._delete_empty_past_file(file_path, current_date, file_type)
            current_date += timedelta(days=1)

def main():
    creator = CalendarFileCreator()
    
    # Find the latest year in the calendar structure
    latest_year = creator._find_latest_year()
    
    creator.clean_empty_files()
    
    # Then create new files from today until December 31st of the latest year
    today = datetime.now()
    end_date = datetime(latest_year, 12, 31)
    
    if end_date < today:
        end_date = datetime(today.year, 12, 31)
    
    creator.create_files_for_range(today, end_date)

if __name__ == "__main__":
    main() 