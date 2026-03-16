package com.vacationplanner.service;

import com.vacationplanner.dto.AuthRequest;
import com.vacationplanner.dto.AuthResponse;
import com.vacationplanner.entity.User;
import com.vacationplanner.repository.UserRepository;
import com.vacationplanner.security.JwtTokenProvider;
import com.vacationplanner.security.UserPrincipal;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

@Service
public class AuthService {

    private final AuthenticationManager authenticationManager;
    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtTokenProvider tokenProvider;

    public AuthService(AuthenticationManager authenticationManager, UserRepository userRepository,
                       PasswordEncoder passwordEncoder, JwtTokenProvider tokenProvider) {
        this.authenticationManager = authenticationManager;
        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;
        this.tokenProvider = tokenProvider;
    }

    public AuthResponse authenticateUser(AuthRequest loginRequest) {
        Authentication authentication = authenticationManager.authenticate(
                new UsernamePasswordAuthenticationToken(
                        loginRequest.email(),
                        loginRequest.password()
                )
        );

        SecurityContextHolder.getContext().setAuthentication(authentication);
        String jwt = tokenProvider.generateToken(authentication);
        
        UserPrincipal userPrincipal = (UserPrincipal) authentication.getPrincipal();
        return new AuthResponse(jwt, userPrincipal.getUsername(), userPrincipal.getDisplayName());
    }

    public AuthResponse registerUser(AuthRequest signUpRequest) {
        if (userRepository.existsByEmail(signUpRequest.email())) {
            throw new RuntimeException("Error: Email is already in use!");
        }

        User user = User.builder()
                .email(signUpRequest.email())
                .password(passwordEncoder.encode(signUpRequest.password()))
                .displayName(signUpRequest.displayName())
                .build();

        userRepository.save(user);
        
        // Auto-login after registration
        return authenticateUser(signUpRequest);
    }
}
