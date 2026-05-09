package com.vacationplanner.dto;

import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import java.util.List;

public record TripRequest(
    @NotBlank String destination,
    @Min(1) @Max(20) int numTravelers,
    @Min(1) @Max(30) int numDays,
    BudgetTier budgetTier,
    Double budgetAmount, // Used when budgetTier is CUSTOM
    Lifestyle lifestyle,
    List<VacationType> vacationTypes,
    String specialRequests
) {}
