package com.TripCraftProject.Services;

import java.time.Duration;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseCookie;
import org.springframework.http.ResponseEntity;
import org.springframework.http.ResponseEntity;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.stereotype.Service;

import com.TripCraftProject.Repository.UserRepo;
import com.TripCraftProject.model.LoginRequest;
import com.TripCraftProject.model.User;

@Service
public class UserService {

    @Autowired
    private JWTService jwtService;

    @Autowired
    AuthenticationManager authManager;

    @Autowired
    private UserRepo repo;
    

    private BCryptPasswordEncoder encoder = new BCryptPasswordEncoder(12);

    public ResponseEntity<String> register(User user) {
    if (repo.findByEmail(user.getEmail()).isPresent()) {
        return ResponseEntity
                .badRequest()
                .body("{\"message\": \"Email already exists\"}");
    }

    user.setPassword(encoder.encode(user.getPassword()));
    user.setProvider("LOCAL");
    repo.save(user);

    return ResponseEntity
            .ok("{\"message\": \"User registered successfully\"}");
}

    public ResponseEntity<Map<String, String>> verify(LoginRequest user) {
        try {
            Authentication authentication = authManager.authenticate(
                    new UsernamePasswordAuthenticationToken(user.getEmail(), user.getPassword()));

            if (authentication.isAuthenticated()) {
                // Generate the JWT token
                String token = jwtService.generateToken(user.getEmail());

                // Create secure cookie
                ResponseCookie cookie = ResponseCookie.from("jwt", token)
                        .httpOnly(true)
                        .secure(false) // Set to true in production with HTTPS
                        .path("/")
                        .maxAge(Duration.ofDays(7))
                        .sameSite("Strict")
                        .build();

                // 🔍 Fetch user by email
                Optional<User> optionalUser = repo.findByEmail(user.getEmail());
                if (optionalUser.isEmpty()) {
                    return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                            .body(Map.of("message", "User not found"));
                }

                User loggedInUser = optionalUser.get();
                String name = loggedInUser.getName();

                               // ✅ JSON response with name
                Map<String, String> responseBody = new HashMap<>();
                responseBody.put("message", "Login successful");
                responseBody.put("name", name);

                return ResponseEntity.ok()
                        .header(HttpHeaders.SET_COOKIE, cookie.toString())
                        .body(responseBody);
            } else {
                return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                        .body(Map.of("message", "Authentication failed"));
            }
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of(
                            "message", "Internal server error: " + e.getMessage(),
                            "status", "error"
                    ));
        }
    }


}
