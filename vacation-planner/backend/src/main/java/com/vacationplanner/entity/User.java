package com.vacationplanner.entity;

import jakarta.persistence.*;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

@Entity
@Table(name = "users")
public class User {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(unique = true, nullable = false)
    private String email;

    @Column(nullable = false)
    private String password; // BCrypt hashed

    private String displayName;

    private LocalDateTime createdAt = LocalDateTime.now();

    @OneToMany(mappedBy = "user", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<SavedItinerary> itineraries = new ArrayList<>();

    public User() {}

    public User(Long id, String email, String password, String displayName, LocalDateTime createdAt, List<SavedItinerary> itineraries) {
        this.id = id;
        this.email = email;
        this.password = password;
        this.displayName = displayName;
        this.createdAt = createdAt != null ? createdAt : LocalDateTime.now();
        this.itineraries = itineraries != null ? itineraries : new ArrayList<>();
    }

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }
    public String getPassword() { return password; }
    public void setPassword(String password) { this.password = password; }
    public String getDisplayName() { return displayName; }
    public void setDisplayName(String displayName) { this.displayName = displayName; }
    public LocalDateTime getCreatedAt() { return createdAt; }
    public void setCreatedAt(LocalDateTime createdAt) { this.createdAt = createdAt; }
    public List<SavedItinerary> getItineraries() { return itineraries; }
    public void setItineraries(List<SavedItinerary> itineraries) { this.itineraries = itineraries; }

    public static UserBuilder builder() {
        return new UserBuilder();
    }

    public static class UserBuilder {
        private String email;
        private String password;
        private String displayName;

        public UserBuilder email(String email) { this.email = email; return this; }
        public UserBuilder password(String password) { this.password = password; return this; }
        public UserBuilder displayName(String displayName) { this.displayName = displayName; return this; }
        public User build() {
            User user = new User();
            user.setEmail(this.email);
            user.setPassword(this.password);
            user.setDisplayName(this.displayName);
            return user;
        }
    }
}
