"""
Logic/itinerary.py
Itinerary generator that schedules destinations into time slots across trip days.
Aligned with Syllabus Unit 2 (OOP, Exceptions) & Unit 3 (Data Structures: Queue).
"""

import sys
from collections import deque
from pathlib import Path
from typing import List, Dict, Any

# Resolve project root for imports
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))


# ==============================================================================
# CUSTOM EXCEPTIONS (Syllabus Unit 2.3)
# ==============================================================================
class ItineraryGenerationError(Exception):
    """Raised when itinerary planning fails due to invalid input or place scarcity."""
    pass


# ==============================================================================
# ITINERARY BUILDER CLASS (Syllabus Unit 2.1 & Unit 3.1)
# ==============================================================================
class ItineraryBuilder:
    """
    Schedules places into morning, afternoon, and evening slots
    using queue structures to prevent duplicates and balance travel days.
    """

    TIME_SLOTS = ("Morning", "Afternoon", "Evening")

    def __init__(self, city: str, days: int, available_places: List[Dict[str, Any]]):
        if days <= 0:
            raise ItineraryGenerationError("Trip days must be at least 1.")
        if not available_places:
            raise ItineraryGenerationError(f"No places supplied to generate itinerary for {city}.")

        self.city = city
        self.days = days
        self.available_places = available_places

    def _segregate_into_slot_queues(self) -> Dict[str, deque]:
        """
        Organizes places into separate deques based on best_time_slot.
        Uses collections.deque (Syllabus Unit 3.1: Queue / Dequeue).
        """
        slot_queues = {
            "Morning": deque(),
            "Afternoon": deque(),
            "Evening": deque()
        }

        # Filter places strictly belonging to the destination city
        city_places = [
            p for p in self.available_places 
            if p.get("city", "").lower() == self.city.lower()
        ]

        if not city_places:
            raise ItineraryGenerationError(f"No destinations found matching city: {self.city}")

        # Populate queues based on optimal slot preference
        for place in city_places:
            slot = place.get("best_time_slot", "Morning")
            if slot in slot_queues:
                slot_queues[slot].append(place)
            else:
                slot_queues["Morning"].append(place)

        return slot_queues

    def build_schedule(self) -> List[Dict[str, Any]]:
        """
        Constructs a structured day-by-day itinerary.
        Dequeues elements round-robin across days to guarantee diverse activities.
        """
        slot_queues = self._segregate_into_slot_queues()
        scheduled_items: List[Dict[str, Any]] = []
        visited_ids = set()

        for day in range(1, self.days + 1):
            for slot in self.TIME_SLOTS:
                target_queue = slot_queues[slot]
                selected_place = None

                # Search through the specific queue for an unvisited place
                rotations = len(target_queue)
                while rotations > 0:
                    candidate = target_queue.popleft()  # Dequeue operation (FIFO)
                    if candidate["id"] not in visited_ids:
                        selected_place = candidate
                        visited_ids.add(candidate["id"])
                        break
                    else:
                        target_queue.append(candidate)  # Rotate back
                    rotations -= 1

                # Fallback: borrow from any other non-empty slot queue if empty
                if not selected_place:
                    for other_slot in self.TIME_SLOTS:
                        while slot_queues[other_slot]:
                            candidate = slot_queues[other_slot].popleft()
                            if candidate["id"] not in visited_ids:
                                selected_place = candidate
                                visited_ids.add(candidate["id"])
                                break
                        if selected_place:
                            break

                # If a place is found, format it into an itinerary item
                if selected_place:
                    scheduled_items.append({
                        "day_number": day,
                        "time_slot": slot,
                        "place_name": selected_place.get("name", "Local Spot"),
                        "category": selected_place.get("category", "General"),
                        "subcategory": selected_place.get("subcategory", ""),
                        "estimated_cost": float(selected_place.get("estimated_cost_inr", 0.0)),
                        "description": selected_place.get("description", "")
                    })

        if not scheduled_items:
            raise ItineraryGenerationError("Could not schedule any itinerary activities.")

        return scheduled_items


if __name__ == "__main__":
    # Quick standalone test
    sample_places = [
        {"id": "TH_01", "name": "Upvan Lake", "city": "Thane", "best_time_slot": "Evening", "estimated_cost_inr": 0},
        {"id": "TH_02", "name": "Yeoor Hills", "city": "Thane", "best_time_slot": "Morning", "estimated_cost_inr": 30},
        {"id": "TH_07", "name": "Mamledar Misal", "city": "Thane", "best_time_slot": "Morning", "estimated_cost_inr": 150},
        {"id": "TH_09", "name": "Metkut Restaurant", "city": "Thane", "best_time_slot": "Afternoon", "estimated_cost_inr": 450},
    ]

    builder = ItineraryBuilder(city="Thane", days=1, available_places=sample_places)
    schedule = builder.build_schedule()
    for item in schedule:
        print(f"Day {item['day_number']} | {item['time_slot']}: {item['place_name']} (₹{item['estimated_cost']})")
