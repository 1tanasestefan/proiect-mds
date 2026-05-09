package com.vacationplanner.dto;

public record AuthRequest(
    String email,
    String password,
    String displayName // nullable, used only for registration
) {}
