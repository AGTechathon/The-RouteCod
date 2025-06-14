package com.TripCraftProject.Services;

import java.util.Optional;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.stereotype.Service;

import com.TripCraftProject.Repository.UserRepo;
import com.TripCraftProject.model.User;
import com.TripCraftProject.model.UserPrincipal;


@Service
public class MyUserDetailsService implements UserDetailsService {

    @Autowired
    private UserRepo userRepo;


    @Override
    public UserDetails loadUserByUsername(String email) throws UsernameNotFoundException {
        Optional<User> user = userRepo.findByEmail(email);
        
        // Check if user is not present
        if (user.isEmpty()) {
            System.out.println("User Not Found");
            throw new UsernameNotFoundException("User not found");
        }
        
        return new UserPrincipal(user.get());
    }  

}
