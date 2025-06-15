package com.TripCraftProject.util;


import jakarta.servlet.http.Cookie;
import jakarta.servlet.http.HttpServletRequest;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;
import org.springframework.web.context.request.RequestContextHolder;
import org.springframework.web.context.request.ServletRequestAttributes;

import com.TripCraftProject.Repository.UserRepo;
import com.TripCraftProject.Services.JWTService;
import com.TripCraftProject.model.User;
import com.TripCraftProject.model.User;

@Component
public class CurrentUserUtil {

    private final JWTService jwtService;
    @Autowired
    private UserRepo userRepository;


    public CurrentUserUtil(JWTService jwtService) {
        this.jwtService = jwtService;
    }

    public String getCurrentUserEmail() {
        HttpServletRequest request = ((ServletRequestAttributes) RequestContextHolder.getRequestAttributes()).getRequest();
        Cookie[] cookies = request.getCookies();
        if (cookies != null) {
            for (Cookie cookie : cookies) {
                if (cookie.getName().equals("jwt")) {
                    String token = cookie.getValue();
                    return jwtService.extractUserName(token);
                }
            }
        }
        throw new RuntimeException("JWT Token not found in cookies");
    }
    public User getCurrentUser() {
        String email = getCurrentUserEmail();
        return userRepository.findByEmail(email).orElseThrow(() -> new RuntimeException("User not found"));
    }

}
