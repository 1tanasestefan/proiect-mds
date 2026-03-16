package com.vacationplanner.repository;

import com.vacationplanner.entity.SavedItinerary;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;

public interface ItineraryRepository extends JpaRepository<SavedItinerary, Long> {
    List<SavedItinerary> findByUserIdOrderByCreatedAtDesc(Long userId);
}
