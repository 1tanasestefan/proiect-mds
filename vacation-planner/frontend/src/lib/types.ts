export type BudgetTier = 'LOW' | 'MEDIUM' | 'LUXURY' | 'CUSTOM';
export type Lifestyle = 'RELAXED' | 'ENERGETIC' | 'NIGHT_OWL' | 'EARLY_BIRD';
export type VacationType = 'PARTYING' | 'SIGHTSEEING' | 'CULINARY' | 'RELAXING' | 'ADVENTURE' | 'CULTURAL';

export interface TripRequest {
  destination: string;
  numTravelers: number;
  numDays: number;
  budgetTier: BudgetTier;
  budgetAmount?: number;
  lifestyle: Lifestyle;
  vacationTypes: VacationType[];
  specialRequests?: string;
}

export interface AuthResponse {
  token: string;
  email: string;
  displayName: string;
}

export interface User {
  email: string;
  displayName: string;
}
