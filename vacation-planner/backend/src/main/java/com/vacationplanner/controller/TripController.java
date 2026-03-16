package com.vacationplanner.controller;

import com.vacationplanner.dto.TripRequest;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/trips")
public class TripController {

    // private final OrchestratorService orchestratorService; // Will be injected in Phase 4
    
    // public TripController(OrchestratorService orchestratorService) { ... }

    @PostMapping("/plan")
    public ResponseEntity<String> planTrip(@RequestBody TripRequest request) {
        // Validation will happen automatically via Spring's @Valid (add to args later)
        // For now, this is just a stub returning echoing the input destination
        return ResponseEntity.ok("{\"status\": \"received\", \"destination\": \"" + request.destination() + "\"}");
    }
    
    @GetMapping("/history")
    public ResponseEntity<String> getTripHistory() {
        return ResponseEntity.ok("[]"); // Stub
    }
}
