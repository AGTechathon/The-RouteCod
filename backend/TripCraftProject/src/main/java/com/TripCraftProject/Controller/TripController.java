package com.TripCraftProject.Controller;

import com.TripCraftProject.Repository.DestinationRepository;
import com.TripCraftProject.Repository.TripRepository;
import com.TripCraftProject.Repository.UserRepo;
import com.TripCraftProject.Services.TripService;
import com.TripCraftProject.model.Destination;
import com.TripCraftProject.model.Trip;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/trips")
public class TripController {
	  @Autowired
	    private TripService tripService;
	@Autowired
    private  TripRepository tripRepository;
	@Autowired
    private  UserRepo userRepository;
       @Autowired
    private ObjectMapper objectMapper;
    @Autowired
    private RestTemplate restTemplate;
    @Autowired
	private DestinationRepository destinationRepository;
   
    @Value("${python.microservice.url:http://localhost:5000/generate_itinerary}")
    private String pythonMicroserviceUrl;
    
    List<String> imageUrls = Arrays.asList(
    		"http://res.cloudinary.com/didg0xpge/image/upload/v1745563965/rh62v2pkxe1iidaq51pp.jpg",
    		 "http://res.cloudinary.com/didg0xpge/image/upload/v1745564280/thq60ytekuxokvhx1tfh.jpg",
    	        "http://res.cloudinary.com/didg0xpge/image/upload/v1745564379/y3yzv80lqmzq0fgstn9f.jpg",
    	        "http://res.cloudinary.com/didg0xpge/image/upload/v1745564411/nr9wvshaewcssiyldq1r.jpg",
    	        "http://res.cloudinary.com/didg0xpge/image/upload/v1745564438/yotejrr4sp6zb6qa4byx.jpg",
    	        "http://res.cloudinary.com/didg0xpge/image/upload/v1745564462/jh6vo0cyrbxuhb1hbboz.jpg",
    	        "http://res.cloudinary.com/didg0xpge/image/upload/v1745564470/lco3idkoelc4rrhgld7t.jpg",
    	        "http://res.cloudinary.com/didg0xpge/image/upload/v1745564485/gw9svacvp16jdnctkv8p.jpg",
    	        "http://res.cloudinary.com/didg0xpge/image/upload/v1745564495/ruqiponckujq6o7l8czk.jpg"
    	 );

    // ✅ Get all trips
    @GetMapping
    public ResponseEntity<?> getUserTrips() {
        String userId = getCurrentUserId(); // from token/session
        System.out.println("UserId"+userId);
        List<Trip> trips = tripService.getTripsForLoggedInUser(userId);
        return ResponseEntity.ok(trips);
    }


    // ✅ Get a single trip by ID
    @GetMapping("/{id}")
    public ResponseEntity<Trip> getTripById(@PathVariable String id) {
        Optional<Trip> trip = tripRepository.findById(id);
        return trip.map(ResponseEntity::ok)
                   .orElseGet(() -> ResponseEntity.notFound().build());
    }

    @GetMapping("/recent")
    public ResponseEntity<List<Trip>> getRecentTrips() {
    	String userId = getCurrentUserId();
        List<Trip> recentTrips = tripRepository.findByUserIdAndEndDateBefore(userId, LocalDate.now());
        return ResponseEntity.ok(recentTrips);
    }
 // ✅ Get upcoming trips of a user
    @GetMapping("/upcoming")
    public ResponseEntity<List<Trip>> getUpcomingTrips() {
    	String userId = getCurrentUserId();
        List<Trip> upcomingTrips = tripRepository.findByUserIdAndStartDateAfter(userId, java.time.LocalDate.now());
        return ResponseEntity.ok(upcomingTrips);
    }

   
    @PostMapping("/create")
    public ResponseEntity<?> createTrip(@RequestBody Trip trip) {

    	String userId = getCurrentUserId(); // Returns email, e.g., "test@example.com"

        // Step 1: Populate non-input fields
        trip.setUserId(userId);
        trip.setAiGenerated(false);
     
        trip.setCreatedAt(LocalDateTime.now());
        String randomThumbnail = imageUrls.get(new Random().nextInt(imageUrls.size()));
        trip.setThumbnail(randomThumbnail);

        System.out.println("Before Save: " + trip);
        Trip savedTrip = tripRepository.save(trip);
        System.out.println("After Save: " + savedTrip);

        // ✅ Fetch the destination and get the list of spots
        Optional<Destination> destinationOpt = destinationRepository.findByDestinationIgnoreCase(trip.getDestination());

        List<Destination.Spot> spots = new ArrayList<>();
        Destination.Hotel lunch = null;
        Destination.Hotel stay = null;

        if (destinationOpt.isPresent()) {
            Destination destination = destinationOpt.get();
            
            // ✅ Spots
            if (destination.getSpots() != null) {
                spots = destination.getSpots();
            }

            // ✅ Hotels (extract Lunch and Stay)
            if (destination.getHotels() != null) {
                for (Destination.Hotel hotel : destination.getHotels()) {
                    if ("Lunch".equalsIgnoreCase(hotel.getStayType()) && lunch == null) {
                        lunch = hotel;
                    } else if ("Stay".equalsIgnoreCase(hotel.getStayType()) && stay == null) {
                        stay = hotel;
                    }
                }
            }
        }


        // ✅ Build the response
        Map<String, Object> response = new HashMap<>();
        response.put("tripId", savedTrip.getId());
        response.put("spots", spots);  // List<Spot>
        response.put("lunch", lunch);  // Single Hotel with stayType="Lunch"
        response.put("stay", stay);    // Single Hotel with stayType="Stay"

       
        return ResponseEntity.ok(response);
    }
  
   // ✅ Update an existing trip
    @PutMapping("/{id}")
    public ResponseEntity<Trip> updateTrip(@PathVariable String id, @RequestBody Trip updatedTrip) {
        if (!tripRepository.existsById(id)) {
            return ResponseEntity.notFound().build();
        }
        updatedTrip.setId(id);  // Ensure the correct ID is set
        Trip savedTrip = tripRepository.save(updatedTrip);
        return ResponseEntity.ok(savedTrip);
    }

    // ✅ Delete a trip
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteTrip(@PathVariable String id) {
        if (!tripRepository.existsById(id)) {
            return ResponseEntity.notFound().build();
        }
        tripRepository.deleteById(id);
        return ResponseEntity.noContent().build();
    }
    public String getCurrentUserId() {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated() || "anonymousUser".equals(authentication.getPrincipal())) {
            System.out.println("No authenticated user found.");
            throw new IllegalStateException("No authenticated user found.");
        }

        Object principal = authentication.getPrincipal();
        System.out.println("Principal: " + principal);

        if (principal instanceof UserDetails) {
            String username = ((UserDetails) principal).getUsername();
            System.out.println("Authenticated user ID (from UserDetails): " + username);
            return username;
        }

        String userId = principal.toString();
        System.out.println("Authenticated user ID (from principal.toString): " + userId);
        return userId;
    }
    
   
}
