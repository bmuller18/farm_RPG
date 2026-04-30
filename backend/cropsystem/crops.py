from datetime import datetime, timedelta

class Crop:
    def __init__(self, name, growt_seconds, reward):
        self.name = name
        self.growth_time = timedelta(seconds=growt_seconds)
        self.reward = reward

        self.planted_at = None
    
    def plant(self):
        if self.planted_at is None:
            self.planted_at = datetime.now()
            print(f"{self.name} plantadp")
    
    def is_ready(self):
        if self.planted_at is None:
            return False

        return datetime.now() - self.planted_at >= self.growth_time
    
    def harvest(self):
        if self.is_ready():
            self.planted_at = None
            print(f"Recolectaste {self.reward}")
            return self.reward
        else:
            print("Todavia no esta listo")
            return None

    def time_remaining(self):
        if self.planted_at is None:
            return 0
        remaining = self.growth_time - (datetime.now() - self.planted_at)
        return max(0, remaining.total_seconds())