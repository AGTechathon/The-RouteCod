package com.TripCraftProject.Repository;

import java.util.List;
import java.util.Optional;

import org.springframework.data.mongodb.repository.MongoRepository;

import com.TripCraftProject.model.Itinerary;


public interface ItineraryRepository extends MongoRepository<Itinerary, String>{
//	List<Itinerary> findByTripId(String tripId);

	 List<Itinerary> findByTripIdIn(List<String> tripIds); 
	 Itinerary findByTripId(String tripId);
}
