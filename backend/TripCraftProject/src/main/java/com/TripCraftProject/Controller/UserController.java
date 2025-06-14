package com.TripCraftProject.Controller;


import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import com.TripCraftProject.Repository.UserRepo;
import com.TripCraftProject.Services.UserService;
import com.TripCraftProject.model.User;

import java.util.HashMap;
import java.util.Map;
import java.util.Optional;

@RestController
@RequestMapping("/api/profile")
public class UserController {

    private final UserService userService;
    private final UserRepo userRepo;
   


    
    public UserController(UserService userService, UserRepo userRepo) {
		super();
		this.userService = userService;
		this.userRepo = userRepo;
	}


	@PutMapping("/{id}")
    public ResponseEntity<?> updateUserProfile(@PathVariable String id, @RequestBody User updatedUser) {
        return userRepo.findById(id).map(existingUser -> {
            existingUser.setName(updatedUser.getName());
            existingUser.setPhone(updatedUser.getPhone());
            existingUser.setEmail(updatedUser.getEmail());
            userRepo.save(existingUser);
            return ResponseEntity.ok(existingUser);
        }).orElseGet(() -> ResponseEntity.notFound().build());
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<?> deleteUserProfile(@PathVariable String id) {
        if (userRepo.existsById(id)) {
            userRepo.deleteById(id);
            return ResponseEntity.ok("User deleted successfully");
        }
        return ResponseEntity.notFound().build();
    }
}
