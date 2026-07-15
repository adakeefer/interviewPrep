
from pathlib import Path
from datetime import datetime

class Log:
    def __init__(self):
        self.timestamp = datetime.fromisoformat("2025-02-01T00:00:00.000000Z")
        self.log_level = ""
        self.service = ""
        self.message = ""

    
    def __str__(self):
        return str(self.timestamp).replace("+00:00", "Z") + " " + self.log_level + " " + self.service + " " + self.message





class Logarithm:
    def __init__(self):
        self.logs = []
        self.LOG_PATH = "logs/"

    def _parse_log(self, input):
        log = Log()

        c = 0
        timestamp = ""
        while input[c] != " ":
            timestamp += input[c]
            c += 1

        log.timestamp = datetime.fromisoformat(timestamp)
        c += 1

        log_level = ""
        while input[c] != " ":
            log_level += input[c]
            c += 1

        log.log_level = log_level
        c += 1

        service = ""
        while input[c] != " ":
            service += input[c]
            c += 1

        log.service = service
        c += 1

        log.message = input[c:]

        self.logs.append(log)
    
    def _add_file_to_index(self, filepath):
        with open(filepath, "r") as f:
            for line in f:
                if line:
                    self._parse_log(line)
    
    def build_index(self):
        log_path = Path(self.LOG_PATH)
        log_paths = list(log_path.iterdir())
        for path in log_paths:
            self._add_file_to_index(path)
        
        self.logs.sort(key=lambda l: (l.timestamp, l.log_level, l.service))
    
    def _timestamp_match(self, log, target_time_start, target_time_end):
        return target_time_start and target_time_end and log.timestamp >= target_time_start and log.timestamp < target_time_end

    def _log_level_match(self, log, target_log_level):
         return target_log_level and log.log_level == target_log_level
    
    def _service_match(self, log, target_service):
         return target_service and log.service == target_service
    
    def search(self, target_log_level = None, target_service = None, target_time_start = None, target_time_end = None):
        res = []
        if not target_log_level and not target_service and not target_time_start and not target_time_end:
            return res
        for log in self.logs:
            if target_log_level and not self._log_level_match(log, target_log_level):
                 continue
            if target_time_start and not self._timestamp_match(log, target_time_start, target_time_end):
                continue
            if target_service and not self._service_match(log, target_service):
                continue

            res.append(str(log))
        
        return res
            



